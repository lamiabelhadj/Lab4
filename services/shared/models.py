from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class LoanApplicationBase(BaseModel):
    amount: float
    duration: int
    income: float


class LoanApplicationCreate(LoanApplicationBase):
    pass


class LoanApplicationResponse(BaseModel):
    application_id: str
    amount: float
    duration: int
    income: float
    status: str
    created_at: str

    class Config:
        from_attributes = True


class LoanApplicationDetail(LoanApplicationResponse):
    id_document: Optional[str] = None
    salary_slip: Optional[str] = None
    contract_path: Optional[str] = None
    amortization_path: Optional[str] = None
    extracted_income: Optional[float] = None


class ProcessingResult(BaseModel):
    application_id: str
    declared_income: float
    extracted_income: float
    monthly_payment: float
    status: str


class ApprovalResult(BaseModel):
    application_id: str
    message: str
    contract: str
    amortization: str
    monthly_payment: float
