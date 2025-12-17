"""
API Gateway - Routes requests to microservices
Port: 8000
"""
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import httpx
import os
from typing import Optional

# Service URLs
APPLICATION_SERVICE = os.getenv("APPLICATION_SERVICE_URL", "http://localhost:8001")
PROCESSING_SERVICE = os.getenv("PROCESSING_SERVICE_URL", "http://localhost:8002")
APPROVAL_SERVICE = os.getenv("APPROVAL_SERVICE_URL", "http://localhost:8003")

app = FastAPI(
    title="Loan Application API Gateway",
    description="Central gateway for loan application microservices",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {
        "message": "Loan Application API Gateway",
        "status": "running",
        "services": {
            "application": APPLICATION_SERVICE,
            "processing": PROCESSING_SERVICE,
            "approval": APPROVAL_SERVICE
        }
    }


@app.get("/health")
async def health_check():
    """Check health of all services"""
    health = {"gateway": "healthy"}
    
    async with httpx.AsyncClient() as client:
        try:
            r = await client.get(f"{APPLICATION_SERVICE}/health", timeout=5.0)
            health["application-service"] = r.json() if r.status_code == 200 else "unhealthy"
        except:
            health["application-service"] = "unreachable"
        
        try:
            r = await client.get(f"{PROCESSING_SERVICE}/health", timeout=5.0)
            health["processing-service"] = r.json() if r.status_code == 200 else "unhealthy"
        except:
            health["processing-service"] = "unreachable"
        
        try:
            r = await client.get(f"{APPROVAL_SERVICE}/health", timeout=5.0)
            health["approval-service"] = r.json() if r.status_code == 200 else "unhealthy"
        except:
            health["approval-service"] = "unreachable"
    
    return health


# ==================== Application Service Routes ====================

@app.post("/api/loan-application")
async def submit_loan_application(
    amount: float = Form(...),
    duration: int = Form(...),
    income: float = Form(...),
    id_document: UploadFile = File(...),
    salary_slip: UploadFile = File(...)
):
    """Submit a new loan application"""
    async with httpx.AsyncClient() as client:
        try:
            files = {
                "id_document": (id_document.filename, await id_document.read(), id_document.content_type),
                "salary_slip": (salary_slip.filename, await salary_slip.read(), salary_slip.content_type),
            }
            data = {
                "amount": str(amount),
                "duration": str(duration),
                "income": str(income),
            }
            
            response = await client.post(
                f"{APPLICATION_SERVICE}/applications",
                files=files,
                data=data,
                timeout=30.0
            )
            
            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail=response.json().get("detail", "Error"))
            
            return response.json()
        except httpx.RequestError as e:
            raise HTTPException(status_code=503, detail=f"Application service unavailable: {str(e)}")


@app.get("/api/loan-applications")
async def get_all_applications():
    """Get all loan applications"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{APPLICATION_SERVICE}/applications", timeout=10.0)
            return response.json()
        except httpx.RequestError as e:
            raise HTTPException(status_code=503, detail=f"Application service unavailable: {str(e)}")


@app.get("/api/loan-application/{application_id}")
async def get_application(application_id: str):
    """Get a specific loan application"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{APPLICATION_SERVICE}/applications/{application_id}",
                timeout=10.0
            )
            if response.status_code == 404:
                raise HTTPException(status_code=404, detail="Application not found")
            return response.json()
        except httpx.RequestError as e:
            raise HTTPException(status_code=503, detail=f"Application service unavailable: {str(e)}")


# ==================== Processing Service Routes ====================

@app.post("/api/loan-application/{application_id}/process")
async def process_application(application_id: str):
    """Process loan application (OCR + income verification)"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{PROCESSING_SERVICE}/process/{application_id}",
                timeout=60.0  # OCR can take time
            )
            
            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail=response.json().get("detail", "Error"))
            
            return response.json()
        except httpx.RequestError as e:
            raise HTTPException(status_code=503, detail=f"Processing service unavailable: {str(e)}")


@app.get("/api/loan-application/{application_id}/verify-income")
async def verify_income(application_id: str):
    """Get income verification details"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{PROCESSING_SERVICE}/verify-income/{application_id}",
                timeout=10.0
            )
            return response.json()
        except httpx.RequestError as e:
            raise HTTPException(status_code=503, detail=f"Processing service unavailable: {str(e)}")


# ==================== Approval Service Routes ====================

@app.post("/api/loan-application/{application_id}/approve")
async def approve_application(application_id: str):
    """Approve loan application and generate documents"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{APPROVAL_SERVICE}/approve/{application_id}",
                timeout=30.0
            )
            
            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail=response.json().get("detail", "Error"))
            
            return response.json()
        except httpx.RequestError as e:
            raise HTTPException(status_code=503, detail=f"Approval service unavailable: {str(e)}")


@app.post("/api/loan-application/{application_id}/reject")
async def reject_application(application_id: str, reason: Optional[str] = None):
    """Reject loan application"""
    async with httpx.AsyncClient() as client:
        try:
            params = {"reason": reason} if reason else {}
            response = await client.post(
                f"{APPROVAL_SERVICE}/reject/{application_id}",
                params=params,
                timeout=10.0
            )
            return response.json()
        except httpx.RequestError as e:
            raise HTTPException(status_code=503, detail=f"Approval service unavailable: {str(e)}")


@app.get("/api/loan-application/{application_id}/contract")
async def download_contract(application_id: str):
    """Download loan contract"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{APPROVAL_SERVICE}/contract/{application_id}",
                timeout=30.0
            )
            
            if response.status_code == 404:
                raise HTTPException(status_code=404, detail="Contract not found")
            
            return StreamingResponse(
                iter([response.content]),
                media_type="application/pdf",
                headers={"Content-Disposition": f"attachment; filename={application_id}_contract.pdf"}
            )
        except httpx.RequestError as e:
            raise HTTPException(status_code=503, detail=f"Approval service unavailable: {str(e)}")


@app.get("/api/loan-application/{application_id}/amortization")
async def download_amortization(application_id: str):
    """Download amortization schedule"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{APPROVAL_SERVICE}/amortization/{application_id}",
                timeout=30.0
            )
            
            if response.status_code == 404:
                raise HTTPException(status_code=404, detail="Amortization schedule not found")
            
            return StreamingResponse(
                iter([response.content]),
                media_type="application/pdf",
                headers={"Content-Disposition": f"attachment; filename={application_id}_amortization.pdf"}
            )
        except httpx.RequestError as e:
            raise HTTPException(status_code=503, detail=f"Approval service unavailable: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
