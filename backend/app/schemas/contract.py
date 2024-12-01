from typing import Optional, List, Dict
from datetime import date
from pydantic import BaseModel, constr, confloat, conint
from ..models.contract import ContractStatus, PaymentFrequency, PaymentMethod

class PaymentBase(BaseModel):
    amount: confloat(gt=0)
    payment_date: date
    due_date: date
    payment_method: str
    transaction_id: Optional[str] = None
    is_late: bool = False
    late_fee: confloat(ge=0) = 0.0
    notes: Optional[str] = None

class PaymentCreate(PaymentBase):
    pass

class Payment(PaymentBase):
    id: int
    contract_id: int
    created_at: date
    updated_at: date

    class Config:
        orm_mode = True

class ContractDocumentBase(BaseModel):
    document_type: str
    file_path: str
    upload_date: date
    is_signed: bool = False
    signed_date: Optional[date] = None

class ContractDocumentCreate(ContractDocumentBase):
    pass

class ContractDocument(ContractDocumentBase):
    id: int
    contract_id: int
    created_at: date
    updated_at: date

    class Config:
        orm_mode = True

class ContractBase(BaseModel):
    contract_number: constr(min_length=1, max_length=50)
    status: ContractStatus = ContractStatus.DRAFT
    start_date: date
    end_date: date
    rent_amount: confloat(gt=0)
    security_deposit: confloat(ge=0)
    payment_frequency: PaymentFrequency = PaymentFrequency.MONTHLY
    payment_due_day: conint(ge=1, le=31)
    payment_method: PaymentMethod = PaymentMethod.TRANSFER
    terms_and_conditions: str
    special_conditions: Optional[str] = None
    is_renewable: bool = True
    renewal_price_increase: Optional[confloat(ge=0, le=100)] = None
    auto_renewal: bool = False
    utilities_included: Optional[Dict[str, bool]] = None
    guarantor_info: Optional[Dict[str, str]] = None

class ContractCreate(ContractBase):
    tenant_id: int
    unit_id: int
    documents: Optional[List[ContractDocumentCreate]] = []

class ContractUpdate(BaseModel):
    status: Optional[ContractStatus] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    rent_amount: Optional[confloat(gt=0)] = None
    security_deposit: Optional[confloat(ge=0)] = None
    payment_frequency: Optional[PaymentFrequency] = None
    payment_due_day: Optional[conint(ge=1, le=31)] = None
    payment_method: Optional[PaymentMethod] = None
    terms_and_conditions: Optional[str] = None
    special_conditions: Optional[str] = None
    is_renewable: Optional[bool] = None
    renewal_price_increase: Optional[confloat(ge=0, le=100)] = None
    auto_renewal: Optional[bool] = None
    deposit_returned: Optional[bool] = None
    deposit_return_date: Optional[date] = None
    deposit_deductions: Optional[confloat(ge=0)] = None
    deposit_notes: Optional[str] = None
    utilities_included: Optional[Dict[str, bool]] = None
    guarantor_info: Optional[Dict[str, str]] = None

class Contract(ContractBase):
    id: int
    tenant_id: int
    unit_id: int
    last_payment_date: Optional[date] = None
    deposit_returned: bool = False
    deposit_return_date: Optional[date] = None
    deposit_deductions: confloat(ge=0) = 0.0
    deposit_notes: Optional[str] = None
    documents: List[ContractDocument] = []
    payments: List[Payment] = []
    created_at: date
    updated_at: date

    class Config:
        orm_mode = True

class ContractInDB(Contract):
    pass

class ContractWithDetails(Contract):
    tenant: "TenantBase"
    unit: "UnitBase"
