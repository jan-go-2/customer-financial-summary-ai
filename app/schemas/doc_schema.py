"""
One Pydantic model per document type, grouped by category to match your
document taxonomy sheet. Field lists start from the "Key Information
Extracted" column and add a few adjacent fields (dates, account/reference
numbers, names) that are normally needed alongside the headline fields.

Add a new document type: define the model in its category section below,
then register it in DOC_TYPE_SCHEMAS. Nothing else needs to change.
"""

from typing import Optional
from pydantic import BaseModel


# ============================================================
# Income Documents
# ============================================================

class SalarySlip(BaseModel):
    employee_name: Optional[str] = None
    company_name: Optional[str] = None
    gross_salary: Optional[str] = None
    net_salary: Optional[str] = None
    deductions: Optional[str] = None
    provident_fund: Optional[str] = None
    pay_period: Optional[str] = None


class Form16(BaseModel):
    employee_name: Optional[str] = None
    employer_name: Optional[str] = None
    pan_number: Optional[str] = None
    assessment_year: Optional[str] = None
    annual_income: Optional[str] = None
    tax_deducted: Optional[str] = None


class IncomeTaxReturn(BaseModel):
    assessee_name: Optional[str] = None
    pan_number: Optional[str] = None
    assessment_year: Optional[str] = None
    total_income: Optional[str] = None
    tax_paid: Optional[str] = None
    filing_date: Optional[str] = None


class BonusLetter(BaseModel):
    employee_name: Optional[str] = None
    company_name: Optional[str] = None
    bonus_amount: Optional[str] = None
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
    total_credits: Optional[str] = None
    total_debits: Optional[str] = None
    average_balance: Optional[str] = None
    salary_credits: Optional[str] = None
    emi_debits: Optional[str] = None


class FixedDepositReceipt(BaseModel):
    depositor_name: Optional[str] = None
    bank_name: Optional[str] = None
    fd_number: Optional[str] = None
    deposit_amount: Optional[str] = None
    deposit_date: Optional[str] = None
    maturity_date: Optional[str] = None
    interest_rate: Optional[str] = None


# ============================================================
# Asset Documents
# ============================================================

class MutualFundStatement(BaseModel):
    investor_name: Optional[str] = None
    folio_number: Optional[str] = None
    fund_name: Optional[str] = None
    units_held: Optional[str] = None
    holdings_value: Optional[str] = None
    statement_date: Optional[str] = None


class DematStatement(BaseModel):
    account_holder_name: Optional[str] = None
    dp_id: Optional[str] = None
    client_id: Optional[str] = None
    holdings_value: Optional[str] = None
    statement_date: Optional[str] = None


class InsurancePolicy(BaseModel):
    policy_holder_name: Optional[str] = None
    policy_number: Optional[str] = None
    insurer_name: Optional[str] = None
    sum_assured: Optional[str] = None
    premium_amount: Optional[str] = None
    policy_start_date: Optional[str] = None
    policy_end_date: Optional[str] = None


# ============================================================
# Liability Documents
# ============================================================

class HomeLoanStatement(BaseModel):
    borrower_name: Optional[str] = None
    lender_name: Optional[str] = None
    loan_account_number: Optional[str] = None
    outstanding_amount: Optional[str] = None
    emi_amount: Optional[str] = None
    loan_start_date: Optional[str] = None
    tenure: Optional[str] = None


class CarLoanStatement(BaseModel):
    borrower_name: Optional[str] = None
    lender_name: Optional[str] = None
    loan_account_number: Optional[str] = None
    outstanding_amount: Optional[str] = None
    emi_amount: Optional[str] = None


class CreditCardStatement(BaseModel):
    card_holder_name: Optional[str] = None
    card_number_masked: Optional[str] = None
    issuing_bank: Optional[str] = None
    outstanding_amount: Optional[str] = None
    credit_limit: Optional[str] = None
    minimum_due: Optional[str] = None
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
    plot_area: Optional[str] = None
    property_status: Optional[str] = None
    sale_consideration: Optional[str] = None
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
    agreement_value: Optional[str] = None
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
    ctc: Optional[str] = None
    joining_date: Optional[str] = None


class PromotionLetter(BaseModel):
    employee_name: Optional[str] = None
    company_name: Optional[str] = None
    new_designation: Optional[str] = None
    revised_salary: Optional[str] = None
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