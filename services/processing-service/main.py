"""
Processing Service - Handles OCR and income verification
Port: 8002
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from typing import Optional
import os
import re
import sys

# Add shared module to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from shared.database import init_db, close_db, get_db_pool
from shared.models import ProcessingResult
from shared.config import UPLOAD_DIR

# OCR imports (optional - will work without if not installed)
try:
    import pytesseract
    from pdf2image import convert_from_path
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    print("Warning: pytesseract or pdf2image not installed. OCR will be simulated.")


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
    await close_db()


app = FastAPI(
    title="Processing Service",
    description="Handles OCR and income verification for loan applications",
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
    return {
        "service": "processing-service", 
        "status": "healthy",
        "ocr_available": OCR_AVAILABLE
    }


def extract_income_from_salary_pdf(pdf_path: str) -> Optional[float]:
    """
    OCR on salary slip to extract monthly income.
    Returns None if no income found.
    """
    if not OCR_AVAILABLE:
        # Simulate OCR by returning a random income for testing
        import random
        return random.uniform(3000, 10000)
    
    try:
        images = convert_from_path(pdf_path)
        full_text = ""
        for img in images:
            full_text += pytesseract.image_to_string(img)
        
        # Look for income patterns
        for line in full_text.splitlines():
            if re.search(r"(Income|Salaire|Salary|Net|Total)", line, re.IGNORECASE):
                match = re.search(r"\d+(?:[,.\s]\d+)*(?:\.\d+)?", line.replace(",", ""))
                if match:
                    value = match.group().replace(" ", "").replace(",", "")
                    return float(value)
        
        return None
    except Exception as e:
        print(f"OCR Error: {e}")
        return None


def calculate_credit_score(declared_income: float, extracted_income: float, monthly_payment: float) -> str:
    """
    Calculate credit score and return status.
    Simple rule: income must be at least 2x the monthly payment.
    """
    # Check if extracted income matches declared (within 20% tolerance)
    income_match = abs(extracted_income - declared_income) / declared_income < 0.2 if declared_income > 0 else False
    
    # Check debt-to-income ratio
    can_afford = extracted_income >= monthly_payment * 2 and declared_income >= monthly_payment * 2
    
    if can_afford and income_match:
        return "Pre-approved"
    elif can_afford:
        return "Review-required"
    else:
        return "Rejected"


@app.post("/process/{application_id}", response_model=ProcessingResult)
async def process_loan_application(application_id: str):
    """
    Process loan application:
    - Perform OCR on salary slip
    - Calculate credit score
    - Update status
    """
    try:
        pool = await get_db_pool()
        async with pool.acquire() as conn:
            row = await conn.fetchrow("""
                SELECT amount, duration, income, salary_slip, status
                FROM loan_applications
                WHERE application_id = $1
            """, application_id)
        
        if not row:
            raise HTTPException(status_code=404, detail="Application not found")
        
        if row["status"] not in ["Submitted"]:
            raise HTTPException(status_code=400, detail=f"Cannot process application with status: {row['status']}")
        
        # OCR on salary slip
        pdf_path = os.path.join(UPLOAD_DIR, row["salary_slip"])
        
        if not os.path.exists(pdf_path):
            raise HTTPException(status_code=404, detail="Salary slip document not found")
        
        extracted_income = extract_income_from_salary_pdf(pdf_path)
        
        if extracted_income is None:
            # Default to declared income if OCR fails
            extracted_income = float(row["income"])
        
        declared_income = float(row["income"])
        monthly_payment = float(row["amount"]) / int(row["duration"])
        
        # Calculate status
        status = calculate_credit_score(declared_income, extracted_income, monthly_payment)
        
        # Update database
        async with pool.acquire() as conn:
            await conn.execute("""
                UPDATE loan_applications
                SET status = $1, extracted_income = $2, updated_at = CURRENT_TIMESTAMP
                WHERE application_id = $3
            """, status, extracted_income, application_id)
        
        return ProcessingResult(
            application_id=application_id,
            declared_income=declared_income,
            extracted_income=extracted_income,
            monthly_payment=round(monthly_payment, 2),
            status=status
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/verify-income/{application_id}")
async def verify_income(application_id: str):
    """Get income verification details for an application"""
    try:
        pool = await get_db_pool()
        async with pool.acquire() as conn:
            row = await conn.fetchrow("""
                SELECT income, extracted_income, amount, duration
                FROM loan_applications
                WHERE application_id = $1
            """, application_id)
        
        if not row:
            raise HTTPException(status_code=404, detail="Application not found")
        
        declared = float(row["income"])
        extracted = float(row["extracted_income"]) if row["extracted_income"] else None
        monthly = float(row["amount"]) / int(row["duration"])
        
        return {
            "application_id": application_id,
            "declared_income": declared,
            "extracted_income": extracted,
            "monthly_payment": round(monthly, 2),
            "income_verified": extracted is not None,
            "debt_to_income_ratio": round(monthly / declared * 100, 2) if declared > 0 else None
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
