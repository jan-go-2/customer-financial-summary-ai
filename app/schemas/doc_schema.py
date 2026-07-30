from typing import Optional
from pydantic import BaseModel


class IdentityDocument(BaseModel):
    name: Optional[str] = None
    date_of_birth: Optional[str] = None
    pan_number: Optional[str] = None
    aadhaar_number: Optional[str] = None
    address: Optional[str] = None


class SalarySlip(BaseModel):
    employee_name: Optional[str] = None
    company_name: Optional[str] = None
    gross_salary: Optional[str] = None
    net_salary: Optional[str] = None
    pay_period: Optional[str] = None


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



DOC_TYPE_SCHEMAS = {
    "identity_document": IdentityDocument,
    "salary_slip": SalarySlip,
    "property_sale_deed": PropertySaleDeed,
}