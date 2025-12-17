<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# Loan Application System - Microservices Architecture

This is a full-stack loan application system with microservices architecture:

## Services

### API Gateway (Port 8000)
- Located in `/services/api-gateway`
- Routes requests to appropriate microservice
- Single entry point for frontend

### Application Service (Port 8001)
- Located in `/services/application-service`
- Handles loan submission and document storage
- CRUD operations on applications

### Processing Service (Port 8002)
- Located in `/services/processing-service`
- OCR on salary slips
- Income verification and credit scoring

### Approval Service (Port 8003)
- Located in `/services/approval-service`
- Contract PDF generation
- Amortization schedule generation

### Shared Module
- Located in `/services/shared`
- Common config, database, and models

## Frontend (React + TypeScript + Vite)
- Located in `/frontend`
- Uses React with TypeScript
- Styled with custom CSS

## Key Technologies
- FastAPI for all backend services
- PostgreSQL with asyncpg
- React 18 with TypeScript
- Docker Compose for orchestration
- reportlab for PDF generation
- pytesseract for OCR

## API Endpoints (via Gateway)
- POST /api/loan-application - Submit loan
- GET /api/loan-applications - Get all
- POST /api/loan-application/{id}/process - OCR & verify
- POST /api/loan-application/{id}/approve - Approve & generate docs
- GET /api/loan-application/{id}/contract - Download contract
- GET /api/loan-application/{id}/amortization - Download amortization
