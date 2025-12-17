"""
Application Service - Handles loan application submission and document storage
Port: 8001
"""
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from typing import List
import os
import uuid
import sys

# Add shared module to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from shared.database import init_db, close_db, get_db_pool, create_tables
from shared.models import LoanApplicationResponse
from shared.config import UPLOAD_DIR

# Create uploads directory
os.makedirs(UPLOAD_DIR, exist_ok=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    await create_tables()
    yield
    await close_db()


app = FastAPI(
    title="Application Service",
    description="Handles loan application submission and document storage",
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
    return {"service": "application-service", "status": "healthy"}


@app.post("/applications", response_model=LoanApplicationResponse)
async def submit_loan_application(
    amount: float = Form(...),
    duration: int = Form(...),
    income: float = Form(...),
    id_document: UploadFile = File(...),
    salary_slip: UploadFile = File(...)
):
    """Submit a new loan application with documents"""
    try:
        # Validate file types
        allowed_extensions = ['.pdf', '.PDF']
        
        id_ext = os.path.splitext(id_document.filename)[1]
        salary_ext = os.path.splitext(salary_slip.filename)[1]
        
        if id_ext not in allowed_extensions or salary_ext not in allowed_extensions:
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")
        
        # Generate unique application ID
        application_id = str(uuid.uuid4())
        
        # Save uploaded files
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
        
        # Insert into database
        pool = await get_db_pool()
        async with pool.acquire() as conn:
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
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/applications", response_model=List[LoanApplicationResponse])
async def get_all_applications():
    """Get all loan applications"""
    try:
        pool = await get_db_pool()
        async with pool.acquire() as conn:
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


@app.get("/applications/{application_id}", response_model=LoanApplicationResponse)
async def get_application(application_id: str):
    """Get a specific loan application"""
    try:
        pool = await get_db_pool()
        async with pool.acquire() as conn:
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


@app.put("/applications/{application_id}/status")
async def update_application_status(application_id: str, status: str):
    """Update application status (internal use)"""
    try:
        pool = await get_db_pool()
        async with pool.acquire() as conn:
            await conn.execute('''
                UPDATE loan_applications 
                SET status = $1, updated_at = CURRENT_TIMESTAMP
                WHERE application_id = $2
            ''', status, application_id)
        return {"message": "Status updated", "status": status}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
