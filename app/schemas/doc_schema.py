import re
from typing import Annotated, Optional
from pydantic import BaseModel, BeforeValidator


_NUMBER_PATTERN = re.compile(r"-?\d[\d,]*(?:\.\d+)?")


def _clean_amount(value):
    """Find the number embedded in messy LLM output and convert to float.
    Returns None if the value is missing or truly not a number, instead
    of raising -- a null amount is normal LLM output, a crash isn't.

    Matches the actual digit sequence rather than stripping character by
    character, so abbreviation punctuation (e.g. the "." in "Rs.") doesn't
    get mistaken for a second decimal point."""
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        match = _NUMBER_PATTERN.search(value)
        if not match:
            return None
        cleaned = match.group().replace(",", "")
        try:
            return float(cleaned)
        except ValueError:
            return None
    return None


Amount = Annotated[Optional[float], BeforeValidator(_clean_amount)]


# ============================================================
# Income Documents
# ============================================================

class SalarySlip(BaseModel):
    employee_name: Optional[str] = None
    company_name: Optional[str] = None
    gross_salary: Amount = None
    net_salary: Amount = None
    deductions: Amount = None
    provident_fund: Amount = None
    pay_period: Optional[str] = None


class Form16(BaseModel):
    employee_name: Optional[str] = None
    employer_name: Optional[str] = None
    pan_number: Optional[str] = None
    assessment_year: Optional[str] = None
    annual_income: Amount = None
    tax_deducted: Amount = None


class IncomeTaxReturn(BaseModel):
    assessee_name: Optional[str] = None
    pan_number: Optional[str] = None
    assessment_year: Optional[str] = None
    total_income: Amount = None
    tax_paid: Amount = None
    filing_date: Optional[str] = None


class BonusLetter(BaseModel):
    employee_name: Optional[str] = None
    company_name: Optional[str] = None
    bonus_amount: Amount = None
    financial_year: Optional[str] = None
    bonus_date: Optional[str] = None


# ============================================================
# Banking Documents
# ============================================================

class BankStatement(BaseModel):
    account_holder_name: Optional[str] = None
    account_number: Optional[str] = None
    bank_name: Optional[str] = None
    statement_period: Optional[str] = None
    total_credits: Amount = None
    total_debits: Amount = None
    average_balance: Amount = None
    salary_credits: Amount = None
    emi_debits: Amount = None


class FixedDepositReceipt(BaseModel):
    depositor_name: Optional[str] = None
    bank_name: Optional[str] = None
    fd_number: Optional[str] = None
    deposit_amount: Amount = None
    deposit_date: Optional[str] = None
    maturity_date: Optional[str] = None
    interest_rate: Amount = None


# ============================================================
# Asset Documents
# ============================================================

class MutualFundStatement(BaseModel):
    investor_name: Optional[str] = None
    folio_number: Optional[str] = None
    fund_name: Optional[str] = None
    units_held: Amount = None
    holdings_value: Amount = None
    statement_date: Optional[str] = None


class DematStatement(BaseModel):
    account_holder_name: Optional[str] = None
    dp_id: Optional[str] = None
    client_id: Optional[str] = None
    holdings_value: Amount = None
    statement_date: Optional[str] = None


class InsurancePolicy(BaseModel):
    policy_holder_name: Optional[str] = None
    policy_number: Optional[str] = None
    insurer_name: Optional[str] = None
    sum_assured: Amount = None
    premium_amount: Amount = None
    policy_start_date: Optional[str] = None
    policy_end_date: Optional[str] = None


# ============================================================
# Liability Documents
# ============================================================

class HomeLoanStatement(BaseModel):
    borrower_name: Optional[str] = None
    lender_name: Optional[str] = None
    loan_account_number: Optional[str] = None
    outstanding_amount: Amount = None
    emi_amount: Amount = None
    loan_start_date: Optional[str] = None
    tenure: Optional[str] = None


class CarLoanStatement(BaseModel):
    borrower_name: Optional[str] = None
    lender_name: Optional[str] = None
    loan_account_number: Optional[str] = None
    outstanding_amount: Amount = None
    emi_amount: Amount = None


class CreditCardStatement(BaseModel):
    card_holder_name: Optional[str] = None
    card_number_masked: Optional[str] = None
    issuing_bank: Optional[str] = None
    outstanding_amount: Amount = None
    credit_limit: Amount = None
    minimum_due: Amount = None
    statement_date: Optional[str] = None


# ============================================================
# Property Documents
# ============================================================

class PropertySaleDeed(BaseModel):
    seller_name: Optional[str] = None
    seller_address: Optional[str] = None
    seller_aadhaar_number: Optional[str] = None
    buyer_name: Optional[str] = None
    buyer_address: Optional[str] = None
    buyer_aadhaar_number: Optional[str] = None
    agreement_date: Optional[str] = None
    property_type: Optional[str] = None
    property_address: Optional[str] = None
    plot_area: Optional[str] = None  # kept as str -- usually includes a unit (sq ft/sq yd), converting to float alone loses that
    property_status: Optional[str] = None
    sale_consideration: Amount = None
    possession_date: Optional[str] = None
    jurisdiction: Optional[str] = None
    registration_number: Optional[str] = None
    survey_number: Optional[str] = None
    witness_1: Optional[str] = None
    witness_2: Optional[str] = None


class PurchaseAgreement(BaseModel):
    buyer_name: Optional[str] = None
    seller_name: Optional[str] = None
    property_address: Optional[str] = None
    agreement_value: Amount = None
    agreement_date: Optional[str] = None
    possession_date: Optional[str] = None


class InheritanceDocument(BaseModel):
    heir_name: Optional[str] = None
    deceased_name: Optional[str] = None
    relationship: Optional[str] = None
    inherited_asset_details: Optional[str] = None
    date_of_inheritance: Optional[str] = None


# ============================================================
# Employment Documents
# ============================================================

class OfferLetter(BaseModel):
    employee_name: Optional[str] = None
    employer_name: Optional[str] = None
    designation: Optional[str] = None
    ctc: Amount = None
    joining_date: Optional[str] = None


class PromotionLetter(BaseModel):
    employee_name: Optional[str] = None
    company_name: Optional[str] = None
    new_designation: Optional[str] = None
    revised_salary: Amount = None
    effective_date: Optional[str] = None


class ExperienceLetter(BaseModel):
    employee_name: Optional[str] = None
    company_name: Optional[str] = None
    designation: Optional[str] = None
    date_of_joining: Optional[str] = None
    date_of_relieving: Optional[str] = None
    employment_duration: Optional[str] = None


# ============================================================
# Identity Documents
# ============================================================

class IdentityDocument(BaseModel):
    """Generic/combined identity model -- kept for backward compatibility.
    For new work, prefer the specific PanCard / AadhaarCard models below."""
    name: Optional[str] = None
    date_of_birth: Optional[str] = None
    pan_number: Optional[str] = None
    aadhaar_number: Optional[str] = None
    address: Optional[str] = None


class PanCard(BaseModel):
    name: Optional[str] = None
    father_name: Optional[str] = None
    pan_number: Optional[str] = None
    date_of_birth: Optional[str] = None


class AadhaarCard(BaseModel):
    name: Optional[str] = None
    aadhaar_number: Optional[str] = None
    date_of_birth: Optional[str] = None
    gender: Optional[str] = None
    address: Optional[str] = None


# ============================================================
# Legal Documents
# ============================================================

class PowerOfAttorney(BaseModel):
    grantor_name: Optional[str] = None
    attorney_name: Optional[str] = None
    authorized_powers: Optional[str] = None
    execution_date: Optional[str] = None
    jurisdiction: Optional[str] = None


class Affidavit(BaseModel):
    deponent_name: Optional[str] = None
    declaration_summary: Optional[str] = None
    execution_date: Optional[str] = None
    notary_details: Optional[str] = None


# ============================================================
# Registry -- add a new document type here after defining its model above
# ============================================================

DOC_TYPE_SCHEMAS = {
    # Income Documents
    "salary_slip": SalarySlip,
    "form_16": Form16,
    "income_tax_return": IncomeTaxReturn,
    "bonus_letter": BonusLetter,

    # Banking Documents
    "bank_statement": BankStatement,
    "fixed_deposit_receipt": FixedDepositReceipt,

    # Asset Documents
    "mutual_fund_statement": MutualFundStatement,
    "demat_statement": DematStatement,
    "insurance_policy": InsurancePolicy,

    # Liability Documents
    "home_loan_statement": HomeLoanStatement,
    "car_loan_statement": CarLoanStatement,
    "credit_card_statement": CreditCardStatement,

    # Property Documents
    "property_sale_deed": PropertySaleDeed,
    "purchase_agreement": PurchaseAgreement,
    "inheritance_document": InheritanceDocument,

    # Employment Documents
    "offer_letter": OfferLetter,
    "promotion_letter": PromotionLetter,
    "experience_letter": ExperienceLetter,

    # Identity Documents
    "identity_document": IdentityDocument,   # generic/combined, kept for backward compatibility
    "pan_card": PanCard,
    "aadhaar_card": AadhaarCard,

    # Legal Documents
    "power_of_attorney": PowerOfAttorney,
    "affidavit": Affidavit,
}