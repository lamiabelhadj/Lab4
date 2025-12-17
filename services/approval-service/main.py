"""
Approval Service - Handles loan approval and document generation
Port: 8003
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
import os
import sys

# Add shared module to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from shared.database import init_db, close_db, get_db_pool
from shared.models import ApprovalResult
from shared.config import UPLOAD_DIR

# PDF generation
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch

os.makedirs(UPLOAD_DIR, exist_ok=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
    await close_db()


app = FastAPI(
    title="Approval Service",
    description="Handles loan approval and document generation",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    return {"service": "approval-service", "status": "healthy"}


def calculate_monthly_payment(principal: float, months: int, annual_rate: float = 0.055) -> float:
    """Calculate monthly payment using standard amortization formula"""
    monthly_rate = annual_rate / 12
    if monthly_rate == 0:
        return principal / months
    return principal * monthly_rate / (1 - (1 + monthly_rate) ** -months)


def generate_contract_pdf(application_id: str, amount: float, duration: int, 
                          monthly_payment: float, income: float) -> str:
    """Generate loan contract PDF"""
    filename = f"{application_id}_contract.pdf"
    filepath = os.path.join(UPLOAD_DIR, filename)
    
    c = canvas.Canvas(filepath, pagesize=letter)
    width, height = letter
    
    # Header
    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(width/2, height - inch, "LOAN CONTRACT")
    
    c.setFont("Helvetica", 12)
    c.drawCentredString(width/2, height - 1.3*inch, f"Application ID: {application_id}")
    
    # Contract details
    y = height - 2*inch
    c.setFont("Helvetica-Bold", 14)
    c.drawString(inch, y, "Loan Details")
    
    c.setFont("Helvetica", 12)
    details = [
        f"Loan Amount: ${amount:,.2f}",
        f"Duration: {duration} months",
        f"Monthly Payment: ${monthly_payment:,.2f}",
        f"Annual Interest Rate: 5.5%",
        f"Total Payment: ${monthly_payment * duration:,.2f}",
        f"Total Interest: ${(monthly_payment * duration) - amount:,.2f}",
        f"Borrower Monthly Income: ${income:,.2f}",
    ]
    
    y -= 30
    for detail in details:
        c.drawString(inch, y, detail)
        y -= 20
    
    # Terms and conditions
    y -= 30
    c.setFont("Helvetica-Bold", 14)
    c.drawString(inch, y, "Terms and Conditions")
    
    c.setFont("Helvetica", 10)
    terms = [
        "1. The borrower agrees to repay the loan in equal monthly installments.",
        "2. Late payments will incur a fee of 5% of the monthly payment.",
        "3. Early repayment is allowed without penalty after 6 months.",
        "4. The interest rate is fixed for the duration of the loan.",
        "5. This contract is governed by applicable financial regulations.",
    ]
    
    y -= 25
    for term in terms:
        c.drawString(inch, y, term)
        y -= 18
    
    # Signature section
    y -= 40
    c.setFont("Helvetica", 12)
    c.drawString(inch, y, "Borrower Signature: _____________________")
    c.drawString(inch, y - 25, "Date: _____________________")
    c.drawString(4*inch, y, "Lender Signature: _____________________")
    c.drawString(4*inch, y - 25, "Date: _____________________")
    
    c.save()
    return filename


def generate_amortization_pdf(application_id: str, amount: float, duration: int,
                               monthly_payment: float) -> str:
    """Generate amortization schedule PDF"""
    filename = f"{application_id}_amortization.pdf"
    filepath = os.path.join(UPLOAD_DIR, filename)
    
    c = canvas.Canvas(filepath, pagesize=letter)
    width, height = letter
    annual_rate = 0.055
    monthly_rate = annual_rate / 12
    
    # Header
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(width/2, height - inch, "AMORTIZATION SCHEDULE")
    
    c.setFont("Helvetica", 10)
    c.drawCentredString(width/2, height - 1.3*inch, f"Application ID: {application_id}")
    c.drawCentredString(width/2, height - 1.5*inch, 
                        f"Principal: ${amount:,.2f} | Duration: {duration} months | Monthly: ${monthly_payment:,.2f}")
    
    # Table header
    y = height - 2*inch
    c.setFont("Helvetica-Bold", 9)
    headers = ["Month", "Payment", "Principal", "Interest", "Balance"]
    x_positions = [0.5*inch, 1.3*inch, 2.5*inch, 3.7*inch, 5*inch]
    
    for header, x in zip(headers, x_positions):
        c.drawString(x, y, header)
    
    # Draw line under header
    c.line(0.4*inch, y - 5, 6.5*inch, y - 5)
    
    # Amortization schedule
    balance = amount
    y -= 20
    c.setFont("Helvetica", 9)
    
    for month in range(1, duration + 1):
        interest = balance * monthly_rate
        principal_payment = monthly_payment - interest
        balance = max(0, balance - principal_payment)
        
        row = [
            str(month),
            f"${monthly_payment:,.2f}",
            f"${principal_payment:,.2f}",
            f"${interest:,.2f}",
            f"${balance:,.2f}"
        ]
        
        for value, x in zip(row, x_positions):
            c.drawString(x, y, value)
        
        y -= 15
        
        # New page if needed
        if y < inch:
            c.showPage()
            c.setFont("Helvetica-Bold", 9)
            for header, x in zip(headers, x_positions):
                c.drawString(x, height - inch, header)
            c.line(0.4*inch, height - inch - 5, 6.5*inch, height - inch - 5)
            y = height - inch - 25
            c.setFont("Helvetica", 9)
    
    # Summary
    y -= 20
    c.setFont("Helvetica-Bold", 10)
    total_paid = monthly_payment * duration
    total_interest = total_paid - amount
    c.drawString(inch, y, f"Total Paid: ${total_paid:,.2f}")
    c.drawString(inch, y - 15, f"Total Interest: ${total_interest:,.2f}")
    
    c.save()
    return filename


@app.post("/approve/{application_id}", response_model=ApprovalResult)
async def approve_loan(application_id: str):
    """
    Approve loan and generate contract + amortization documents
    """
    try:
        pool = await get_db_pool()
        async with pool.acquire() as conn:
            loan = await conn.fetchrow("""
                SELECT amount, duration, income, status
                FROM loan_applications 
                WHERE application_id = $1
            """, application_id)
        
        if not loan:
            raise HTTPException(status_code=404, detail="Application not found")
        
        if loan["status"] not in ["Pre-approved", "Submitted", "Review-required"]:
            raise HTTPException(
                status_code=400, 
                detail=f"Cannot approve application with status: {loan['status']}"
            )
        
        principal = float(loan["amount"])
        months = loan["duration"]
        income = float(loan["income"])
        
        # Calculate monthly payment
        monthly_payment = calculate_monthly_payment(principal, months)
        
        # Generate PDFs
        contract_filename = generate_contract_pdf(
            application_id, principal, months, monthly_payment, income
        )
        amortization_filename = generate_amortization_pdf(
            application_id, principal, months, monthly_payment
        )
        
        # Update database
        async with pool.acquire() as conn:
            await conn.execute("""
                UPDATE loan_applications 
                SET status = $1, contract_path = $2, amortization_path = $3, 
                    updated_at = CURRENT_TIMESTAMP
                WHERE application_id = $4
            """, "Approved", contract_filename, amortization_filename, application_id)
        
        return ApprovalResult(
            application_id=application_id,
            message="Loan approved successfully",
            contract=contract_filename,
            amortization=amortization_filename,
            monthly_payment=round(monthly_payment, 2)
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/reject/{application_id}")
async def reject_loan(application_id: str, reason: str = "Does not meet criteria"):
    """Reject a loan application"""
    try:
        pool = await get_db_pool()
        async with pool.acquire() as conn:
            await conn.execute("""
                UPDATE loan_applications 
                SET status = $1, updated_at = CURRENT_TIMESTAMP
                WHERE application_id = $2
            """, "Rejected", application_id)
        
        return {"application_id": application_id, "status": "Rejected", "reason": reason}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/contract/{application_id}")
async def download_contract(application_id: str):
    """Download loan contract PDF"""
    filepath = os.path.join(UPLOAD_DIR, f"{application_id}_contract.pdf")
    
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Contract not found")
    
    return FileResponse(
        filepath, 
        media_type="application/pdf", 
        filename=f"{application_id}_contract.pdf"
    )


@app.get("/amortization/{application_id}")
async def download_amortization(application_id: str):
    """Download amortization schedule PDF"""
    filepath = os.path.join(UPLOAD_DIR, f"{application_id}_amortization.pdf")
    
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Amortization schedule not found")
    
    return FileResponse(
        filepath, 
        media_type="application/pdf", 
        filename=f"{application_id}_amortization.pdf"
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
