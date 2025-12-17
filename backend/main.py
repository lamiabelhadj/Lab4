from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List
import os
from datetime import datetime
import uuid
from dotenv import load_dotenv
import os
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List
from reportlab.pdfgen import canvas
import asyncpg
from contextlib import asynccontextmanager


db_pool = None

load_dotenv(dotenv_path="env.example")  


DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:1234@localhost:5432/loandb"
)


UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@asynccontextmanager
async def lifespan(app: FastAPI):

    global db_pool
    db_pool = await asyncpg.create_pool(DATABASE_URL, min_size=1, max_size=10)

    async with db_pool.acquire() as conn:
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS loan_applications (
                id SERIAL PRIMARY KEY,
                application_id VARCHAR(255) UNIQUE NOT NULL,
                amount DECIMAL(12, 2) NOT NULL,
                duration INTEGER NOT NULL,
                income DECIMAL(12, 2) NOT NULL,
                id_document VARCHAR(255),
                salary_slip VARCHAR(255),
                status VARCHAR(50) DEFAULT 'Submitted',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
    
    yield
    

    await db_pool.close()


app = FastAPI(title="Loan Application API", lifespan=lifespan)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class LoanApplicationResponse(BaseModel):
    application_id: str
    amount: float
    duration: int
    income: float
    status: str
    created_at: str


@app.get("/")
async def root():
    return {"message": "Loan Application API", "status": "running"}


@app.post("/api/loan-application", response_model=LoanApplicationResponse)
async def submit_loan_application(
    amount: float = Form(...),
    duration: int = Form(...),
    income: float = Form(...),
    id_document: UploadFile = File(...),
    salary_slip: UploadFile = File(...)
):
    """
    Submit a loan application with documents
    """
    try:

        allowed_extensions = ['.pdf', '.PDF']
        
        id_ext = os.path.splitext(id_document.filename)[1]
        salary_ext = os.path.splitext(salary_slip.filename)[1]
        
        if id_ext not in allowed_extensions or salary_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail="Only PDF files are allowed"
            )
        

        application_id = str(uuid.uuid4())
    
        id_filename = f"{application_id}_id{id_ext}"
        salary_filename = f"{application_id}_salary{salary_ext}"
        
        id_path = os.path.join(UPLOAD_DIR, id_filename)
        salary_path = os.path.join(UPLOAD_DIR, salary_filename)
        
   
        with open(id_path, "wb") as f:
            content = await id_document.read()
            f.write(content)
        
        with open(salary_path, "wb") as f:
            content = await salary_slip.read()
            f.write(content)
        

        async with db_pool.acquire() as conn:
            result = await conn.fetchrow('''
                INSERT INTO loan_applications 
                (application_id, amount, duration, income, id_document, salary_slip, status)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
                RETURNING application_id, amount, duration, income, status, created_at
            ''', application_id, amount, duration, income, id_filename, salary_filename, "Submitted")
        
        return LoanApplicationResponse(
            application_id=result['application_id'],
            amount=float(result['amount']),
            duration=result['duration'],
            income=float(result['income']),
            status=result['status'],
            created_at=result['created_at'].isoformat()
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/loan-applications", response_model=List[LoanApplicationResponse])
async def get_loan_applications():
    """
    Get all loan applications
    """
    try:
        async with db_pool.acquire() as conn:
            rows = await conn.fetch('''
                SELECT application_id, amount, duration, income, status, created_at
                FROM loan_applications
                ORDER BY created_at DESC
            ''')
        
        return [
            LoanApplicationResponse(
                application_id=row['application_id'],
                amount=float(row['amount']),
                duration=row['duration'],
                income=float(row['income']),
                status=row['status'],
                created_at=row['created_at'].isoformat()
            )
            for row in rows
        ]
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/loan-application/{application_id}", response_model=LoanApplicationResponse)
async def get_loan_application(application_id: str):
    """
    Get a specific loan application
    """
    try:
        async with db_pool.acquire() as conn:
            row = await conn.fetchrow('''
                SELECT application_id, amount, duration, income, status, created_at
                FROM loan_applications
                WHERE application_id = $1
            ''', application_id)
        
        if not row:
            raise HTTPException(status_code=404, detail="Application not found")
        
        return LoanApplicationResponse(
            application_id=row['application_id'],
            amount=float(row['amount']),
            duration=row['duration'],
            income=float(row['income']),
            status=row['status'],
            created_at=row['created_at'].isoformat()
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@app.post("/api/loan-application/{application_id}/approve")
async def approve_loan(application_id: str):
    async with db_pool.acquire() as conn:
        loan = await conn.fetchrow("SELECT * FROM loan_applications WHERE application_id=$1", application_id)
        if not loan:
            raise HTTPException(404, "Application not found")
        if loan["status"] != "Submitted":
            raise HTTPException(400, "Cannot approve this status")

        principal = float(loan["amount"])
        months = loan["duration"]
        rate = 0.055
        monthly_rate = rate / 12
        monthly_payment = principal * monthly_rate / (1 - (1 + monthly_rate) ** -months)

        # Génération PDF contrat
        contract_path = os.path.join(UPLOAD_DIR, f"{application_id}_contract.pdf")
        c = canvas.Canvas(contract_path)
        c.drawString(100, 700, f"Loan Contract for {application_id}")
        c.drawString(100, 680, f"Amount: {principal}, Duration: {months}, Monthly: {monthly_payment:.2f}")
        c.save()

        # Génération PDF tableau amortissement
        amort_path = os.path.join(UPLOAD_DIR, f"{application_id}_amortization.pdf")
        c = canvas.Canvas(amort_path)
        c.drawString(100, 700, f"Amortization Schedule for {application_id}")
        balance = principal
        y = 680
        for i in range(1, months + 1):
            interest = balance * monthly_rate
            principal_payment = monthly_payment - interest
            balance -= principal_payment
            c.drawString(100, y, f"Month {i}: Payment {monthly_payment:.2f}, Principal {principal_payment:.2f}, Interest {interest:.2f}, Balance {balance:.2f}")
            y -= 15
            if y < 50:
                c.showPage()
                y = 700
        c.save()

        # Mettre à jour statut et stocker chemins
        await conn.execute("UPDATE loan_applications SET status=$1, id_document=$2, salary_slip=$3 WHERE application_id=$4",
                           "Approved", contract_path, amort_path, application_id)

        return {"message": "Loan approved", "contract": contract_path, "amortization": amort_path}


@app.get("/api/loan-application/{application_id}/contract")
async def download_contract(application_id: str):
    path = os.path.join(UPLOAD_DIR, f"{application_id}_contract.pdf")
    if not os.path.exists(path):
        raise HTTPException(404, "Contract not found")
    return FileResponse(path, media_type="application/pdf", filename=f"{application_id}_contract.pdf")


@app.get("/api/loan-application/{application_id}/amortization")
async def download_amortization(application_id: str):
    path = os.path.join(UPLOAD_DIR, f"{application_id}_amortization.pdf")
    if not os.path.exists(path):
        raise HTTPException(404, "Amortization not found")
    return FileResponse(path, media_type="application/pdf", filename=f"{application_id}_amortization.pdf")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
