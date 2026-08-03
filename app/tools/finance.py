# def calculate_net_worth(entities):
    # pass
    
    
    
from __future__ import annotations

from collections import defaultdict
from decimal import Decimal

from app.schemas.events import FinancialEvent


def money_amount(money) -> Decimal:
    if money is None or money.amount is None:
        return Decimal("0")

    return Decimal(str(money.amount))


def calculate_financial_position(
    events: list[FinancialEvent],
) -> dict:
    current_properties = {}
    liquid_assets = []
    liabilities = []

    for event in events:
        property_name = (
            event.property_description
            or "Unspecified property"
        )

        if event.event_type == "property_inheritance":
            value = (
                money_amount(event.current_documented_value)
                or money_amount(event.inherited_value)
            )

            currency = (
                event.current_documented_value.currency
                if event.current_documented_value
                else (
                    event.inherited_value.currency
                    if event.inherited_value
                    else "UNKNOWN"
                )
            )

            current_properties[property_name] = {
                "asset_type": "property",
                "description": property_name,
                "value": float(value),
                "currency": currency,
                "source_event_id": event.event_id
            }

        elif event.event_type == "property_purchase":
            value = (
                money_amount(event.current_documented_value)
                or money_amount(event.purchase_price)
            )

            currency = (
                event.current_documented_value.currency
                if event.current_documented_value
                else (
                    event.purchase_price.currency
                    if event.purchase_price
                    else "UNKNOWN"
                )
            )

            current_properties[property_name] = {
                "asset_type": "property",
                "description": property_name,
                "value": float(value),
                "currency": currency,
                "source_event_id": event.event_id
            }

            mortgage = money_amount(
                event.outstanding_liability
            )

            if mortgage > 0:
                liabilities.append({
                    "liability_type": "mortgage",
                    "description": property_name,
                    "amount": float(mortgage),
                    "currency": (
                        event.outstanding_liability.currency
                        if event.outstanding_liability
                        else currency
                    ),
                    "source_event_id": event.event_id
                })

        elif event.event_type == "property_sale":
            current_properties.pop(
                property_name,
                None
            )

            sale_price = money_amount(
                event.sale_price
            )

            loan_repaid = money_amount(
                event.outstanding_liability
            )

            net_sale_proceeds = max(
                sale_price - loan_repaid,
                Decimal("0")
            )

            currency = (
                event.sale_price.currency
                if event.sale_price
                else "UNKNOWN"
            )

            liquid_assets.append({
                "asset_type": "documented_sale_proceeds",
                "description": (
                    f"Net proceeds from sale of {property_name}"
                ),
                "value": float(net_sale_proceeds),
                "currency": currency,
                "source_event_id": event.event_id
            })

        elif event.event_type == "gift_received":
            gift_value = money_amount(
                event.gifted_value
            )

            if gift_value > 0:
                liquid_assets.append({
                    "asset_type": "gifted_asset",
                    "description": (
                        event.property_description
                        or "Gifted asset"
                    ),
                    "value": float(gift_value),
                    "currency": (
                        event.gifted_value.currency
                        if event.gifted_value
                        else "UNKNOWN"
                    ),
                    "source_event_id": event.event_id
                })

    asset_ledger = (
        list(current_properties.values())
        + liquid_assets
    )

    totals = defaultdict(
        lambda: {
            "assets": Decimal("0"),
            "liabilities": Decimal("0")
        }
    )

    for asset in asset_ledger:
        totals[asset["currency"]]["assets"] += Decimal(
            str(asset["value"])
        )

    for liability in liabilities:
        totals[liability["currency"]]["liabilities"] += Decimal(
            str(liability["amount"])
        )

    net_worth_by_currency = {}

    for currency, values in totals.items():
        net_worth_by_currency[currency] = {
            "documented_assets": float(
                values["assets"]
            ),
            "documented_liabilities": float(
                values["liabilities"]
            ),
            "estimated_documented_net_worth": float(
                values["assets"] - values["liabilities"]
            )
        }

    return {
        "asset_ledger": asset_ledger,
        "liability_ledger": liabilities,
        "net_worth_by_currency": net_worth_by_currency,
        "limitations": [
            "Historical salary is not counted as an asset.",
            "Historical business income is not automatically counted as an asset.",
            "No currency conversion is performed.",
            "No current property value is inferred unless documented.",
            "Sale proceeds require bank evidence to confirm current availability."
        ]
    }