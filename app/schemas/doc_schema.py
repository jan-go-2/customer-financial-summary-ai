import re
import datetime as _dt
from typing import Annotated, Optional
from pydantic import BaseModel, BeforeValidator
from dateutil import parser as _date_parser


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


# Full ISO-ish date, unambiguous because the year comes first: YYYY-MM-DD or YYYY/MM/DD.
_ISO_DATE_PATTERN = re.compile(r"^(\d{4})[-/](\d{1,2})[-/](\d{1,2})$")

# Year + one more numeric group: YYYY-MM or MM-YYYY.
_YEAR_MONTH_PATTERN = re.compile(r"^(\d{4})[-/](\d{1,2})$")
_MONTH_YEAR_NUMERIC_PATTERN = re.compile(r"^(\d{1,2})[-/](\d{4})$")

# "2022-23", "FY2022-23" style financial-year ranges -- left untouched, since
# "23" here means "year '23", not a month or day.
_YEAR_RANGE_PATTERN = re.compile(r"^(?:FY\s*)?\d{4}\s*[-/]\s*\d{2,4}$", re.IGNORECASE)

# Bare 4-digit year, e.g. "2022".
_YEAR_ONLY_PATTERN = re.compile(r"^\d{4}$")

# Month name + year, e.g. "July 2022", "Jul. 2022".
_MONTH_NAME_YEAR_PATTERN = re.compile(r"^[A-Za-z]+\.?\s+\d{4}$")


def _clean_date(value):
    """Normalize messy LLM date output to ISO 'YYYY-MM-DD'.

    - Month + year only (e.g. "July 2022", "2022-07") -> day defaults to 01:
      "2022-07-01"
    - Year only (e.g. "2022") -> month and day default to 01: "2022-01-01"
    - Year-range/FY style (e.g. "2022-23") -> left unchanged, since it isn't
      a single calendar date at all
    - Any other recognizable date -> normalized to "YYYY-MM-DD" (day-first,
      since that's the common convention in Indian documents)
    - Anything that isn't a real date (missing, "N/A", garbled OCR text,
      etc.) -> None, same philosophy as _clean_amount: a null date is
      normal LLM output, a crash isn't, and keeping junk text around isn't
      useful either
    """
    if value is None:
        return None
    if isinstance(value, (_dt.date, _dt.datetime)):
        return value.strftime("%Y-%m-%d")
    if not isinstance(value, str):
        return None

    text = value.strip()
    if not text:
        return None

    # Already unambiguous YYYY-MM-DD / YYYY/MM/DD -- parse directly rather
    # than through dateutil, which can otherwise flip month/day here.
    m = _ISO_DATE_PATTERN.match(text)
    if m:
        year, month, day = int(m.group(1)), int(m.group(2)), int(m.group(3))
        try:
            return _dt.date(year, month, day).strftime("%Y-%m-%d")
        except ValueError:
            return None

    m = _YEAR_MONTH_PATTERN.match(text)  # YYYY-MM
    if m:
        year, month = int(m.group(1)), int(m.group(2))
        if 1 <= month <= 12:
            return f"{year:04d}-{month:02d}-01"
        return text  # second part isn't a valid month -> treat as FY range

    m = _MONTH_YEAR_NUMERIC_PATTERN.match(text)  # MM-YYYY
    if m:
        month, year = int(m.group(1)), int(m.group(2))
        if 1 <= month <= 12:
            return f"{year:04d}-{month:02d}-01"
        # falls through to generic parsing below if not a valid month

    if _YEAR_RANGE_PATTERN.match(text):
        return text

    if _YEAR_ONLY_PATTERN.match(text):
        return f"{text}-01-01"

    if _MONTH_NAME_YEAR_PATTERN.match(text):
        try:
            parsed = _date_parser.parse(text, default=_dt.datetime(1900, 1, 1))
            return parsed.strftime("%Y-%m-01")
        except (ValueError, OverflowError, TypeError):
            return None

    try:
        parsed = _date_parser.parse(text, dayfirst=True, fuzzy=True)
        return parsed.strftime("%Y-%m-%d")
    except (ValueError, OverflowError, TypeError):
        return None


Date = Annotated[Optional[str], BeforeValidator(_clean_date)]


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
    pay_period: Date = None


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
    filing_date: Date = None


class BonusLetter(BaseModel):
    employee_name: Optional[str] = None
    company_name: Optional[str] = None
    bonus_amount: Amount = None
    financial_year: Optional[str] = None
    bonus_date: Date = None


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
    deposit_date: Date = None
    maturity_date: Date = None
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
    statement_date: Date = None


class DematStatement(BaseModel):
    account_holder_name: Optional[str] = None
    dp_id: Optional[str] = None
    client_id: Optional[str] = None
    holdings_value: Amount = None
    statement_date: Date = None


class InsurancePolicy(BaseModel):
    policy_holder_name: Optional[str] = None
    policy_number: Optional[str] = None
    insurer_name: Optional[str] = None
    sum_assured: Amount = None
    premium_amount: Amount = None
    policy_start_date: Date = None
    policy_end_date: Date = None


# ============================================================
# Liability Documents
# ============================================================

class HomeLoanStatement(BaseModel):
    borrower_name: Optional[str] = None
    lender_name: Optional[str] = None
    loan_account_number: Optional[str] = None
    outstanding_amount: Amount = None
    emi_amount: Amount = None
    loan_start_date: Date = None
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
    statement_date: Date = None


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
    agreement_date: Date = None
    property_type: Optional[str] = None
    property_address: Optional[str] = None
    plot_area: Optional[str] = None  # kept as str -- usually includes a unit (sq ft/sq yd), converting to float alone loses that
    property_status: Optional[str] = None
    sale_consideration: Amount = None
    possession_date: Date = None
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
    agreement_date: Date = None
    possession_date: Date = None


class InheritanceDocument(BaseModel):
    heir_name: Optional[str] = None
    deceased_name: Optional[str] = None
    relationship: Optional[str] = None
    inherited_asset_details: Optional[str] = None
    date_of_inheritance: Date = None


# ============================================================
# Employment Documents
# ============================================================

class OfferLetter(BaseModel):
    employee_name: Optional[str] = None
    employer_name: Optional[str] = None
    designation: Optional[str] = None
    ctc: Amount = None
    joining_date: Date = None


class PromotionLetter(BaseModel):
    employee_name: Optional[str] = None
    company_name: Optional[str] = None
    new_designation: Optional[str] = None
    revised_salary: Amount = None
    effective_date: Date = None


class ExperienceLetter(BaseModel):
    employee_name: Optional[str] = None
    company_name: Optional[str] = None
    designation: Optional[str] = None
    date_of_joining: Date = None
    date_of_relieving: Date = None
    employment_duration: Optional[str] = None


class RelievingLetter(BaseModel):
    """Issued when an employee exits an organization -- distinct from
    ExperienceLetter, which summarizes the full tenure worked."""
    employee_name: Optional[str] = None
    company_name: Optional[str] = None
    designation: Optional[str] = None
    date_of_joining: Date = None
    last_working_day: Date = None
    relieving_date: Date = None
    reason_for_leaving: Optional[str] = None


# ============================================================
# Identity Documents
# ============================================================

class IdentityDocument(BaseModel):
    """Generic/combined identity model -- kept for backward compatibility.
    For new work, prefer the specific PanCard / AadhaarCard models below."""
    name: Optional[str] = None
    date_of_birth: Date = None
    pan_number: Optional[str] = None
    aadhaar_number: Optional[str] = None
    address: Optional[str] = None


class PanCard(BaseModel):
    name: Optional[str] = None
    father_name: Optional[str] = None
    pan_number: Optional[str] = None
    date_of_birth: Date = None


class AadhaarCard(BaseModel):
    name: Optional[str] = None
    aadhaar_number: Optional[str] = None
    date_of_birth: Date = None
    gender: Optional[str] = None
    address: Optional[str] = None


# ============================================================
# Legal Documents
# ============================================================

class PowerOfAttorney(BaseModel):
    grantor_name: Optional[str] = None
    attorney_name: Optional[str] = None
    authorized_powers: Optional[str] = None
    execution_date: Date = None
    jurisdiction: Optional[str] = None


class Affidavit(BaseModel):
    deponent_name: Optional[str] = None
    declaration_summary: Optional[str] = None
    execution_date: Date = None
    notary_details: Optional[str] = None


class LastWillTestament(BaseModel):
    """A will -- specifies how a person's assets are to be distributed
    after death. Distinct from InheritanceDocument, which records an
    heir's already-received inheritance rather than the testator's
    distribution instructions."""
    testator_name: Optional[str] = None
    beneficiaries: Optional[str] = None
    executor_name: Optional[str] = None
    asset_details: Optional[str] = None
    execution_date: Date = None
    witness_1: Optional[str] = None
    witness_2: Optional[str] = None
    registration_number: Optional[str] = None


class GuardianConsentKYCDeclaration(BaseModel):
    """Combined guardian-consent + KYC-declaration document (e.g. for a
    minor's account/investment). Kept as a single schema per current
    requirements -- split into separate GuardianConsentForm and
    KYCDeclaration schemas later if the two ever need to be tracked
    independently."""
    guardian_name: Optional[str] = None
    minor_name: Optional[str] = None
    relationship_to_minor: Optional[str] = None
    customer_name: Optional[str] = None
    identity_number: Optional[str] = None
    consent_date: Date = None
    declaration_date: Date = None
    declaration_summary: Optional[str] = None


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
    "relieving_letter": RelievingLetter,

    # Identity Documents
    "identity_document": IdentityDocument,   # generic/combined, kept for backward compatibility
    "pan_card": PanCard,
    "aadhaar_card": AadhaarCard,

    # Legal Documents
    "power_of_attorney": PowerOfAttorney,
    "affidavit": Affidavit,
    "last_will_testament": LastWillTestament,
    "guardian_consent_kyc_declaration": GuardianConsentKYCDeclaration,
}