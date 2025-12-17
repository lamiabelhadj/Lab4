from sqlalchemy import Column, Integer, String, Numeric, DateTime
from sqlalchemy.sql import func
from app.database import Base

class LoanApplication(Base):
    __tablename__ = "loan_applications"

    id = Column(Integer, primary_key=True, index=True)
    client_name = Column(String(255), nullable=False)
    client_email = Column(String(255), nullable=False)
    loan_amount = Column(Numeric(12, 2), nullable=False)
    duration_months = Column(Integer, nullable=False)
    interest_rate = Column(Numeric(5, 2), default=5.5)
    status = Column(String(50), default='SUBMITTED')  # SUBMITTED, COMMERCIAL_APPROVED, RISK_APPROVED, APPROVED, REJECTED
    contract_path = Column(String(500), nullable=True)
    amortization_path = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    approved_at = Column(DateTime(timezone=True), nullable=True)
