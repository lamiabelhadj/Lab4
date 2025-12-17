# Loan Application System - Microservices Architecture

A full-stack loan application system built with React frontend and FastAPI microservices backend.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend (React)                        │
│                        http://localhost:5173                    │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      API Gateway (Port 8000)                    │
│                   Routes requests to services                   │
└───────┬─────────────────────┬─────────────────────┬─────────────┘
        │                     │                     │
        ▼                     ▼                     ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│  Application  │   │  Processing   │   │   Approval    │
│   Service     │   │   Service     │   │   Service     │
│  (Port 8001)  │   │  (Port 8002)  │   │  (Port 8003)  │
├───────────────┤   ├───────────────┤   ├───────────────┤
│ • Submit loan │   │ • OCR salary  │   │ • Approve loan│
│ • Get loans   │   │ • Verify income│  │ • Gen contract│
│ • Store docs  │   │ • Credit score│   │ • Amortization│
└───────┬───────┘   └───────┬───────┘   └───────┬───────┘
        │                   │                   │
        └───────────────────┼───────────────────┘
                            ▼
              ┌─────────────────────────┐
              │   PostgreSQL Database   │
              │      (Port 5432)        │
              └─────────────────────────┘
```

## 📁 Project Structure

```
Lab4/
├── services/
│   ├── api-gateway/           # Routes requests (Port 8000)
│   │   ├── main.py
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   ├── application-service/   # Loan submission (Port 8001)
│   │   ├── main.py
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   ├── processing-service/    # OCR & verification (Port 8002)
│   │   ├── main.py
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   ├── approval-service/      # Contract generation (Port 8003)
│   │   ├── main.py
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   └── shared/                # Shared modules
│       ├── config.py
│       ├── database.py
│       └── models.py
├── frontend/                  # React application
├── docker-compose.yml         # Container orchestration
├── start-services.bat         # Start all services (Windows)
├── install-services.bat       # Install dependencies
└── README.md
```

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- Node.js 18+
- PostgreSQL (or Docker)

### Option 1: Local Development

1. **Create and setup database:**
```sql
CREATE DATABASE loandb;
```

2. **Install all service dependencies:**
```bash
install-services.bat
```

3. **Start all microservices:**
```bash
start-services.bat
```

4. **Start frontend:**
```bash
cd frontend
npm install
npm run dev
```

### Option 2: Docker Compose

```bash
docker-compose up --build
```

## 🔌 API Endpoints

### API Gateway (http://localhost:8000)

| Method | Endpoint | Description | Service |
|--------|----------|-------------|---------|
| POST | `/api/loan-application` | Submit loan application | Application |
| GET | `/api/loan-applications` | Get all applications | Application |
| GET | `/api/loan-application/{id}` | Get specific application | Application |
| POST | `/api/loan-application/{id}/process` | Process (OCR + verify) | Processing |
| GET | `/api/loan-application/{id}/verify-income` | Get income verification | Processing |
| POST | `/api/loan-application/{id}/approve` | Approve & generate docs | Approval |
| POST | `/api/loan-application/{id}/reject` | Reject application | Approval |
| GET | `/api/loan-application/{id}/contract` | Download contract PDF | Approval |
| GET | `/api/loan-application/{id}/amortization` | Download amortization PDF | Approval |
| GET | `/health` | Health check all services | Gateway |

## 🔄 Workflow

1. **Use Case 1 - Submit Application**
   - Client fills form (amount, duration, income)
   - Client uploads PDF documents (ID + salary slip)
   - Application Service stores data & documents
   - Status: `Submitted`

2. **Use Case 2 - Process Application**
   - Processing Service performs OCR on salary slip
   - Extracts income and verifies against declared
   - Calculates credit score
   - Status: `Pre-approved` | `Review-required` | `Rejected`

3. **Use Case 3 - Approve Loan**
   - Approval Service generates loan contract PDF
   - Generates amortization schedule PDF
   - Status: `Approved`

## 🛠️ Services Details

### Application Service (Port 8001)
- Handles loan submission
- Stores uploaded documents
- CRUD operations on applications

### Processing Service (Port 8002)
- OCR on salary slips (pytesseract + pdf2image)
- Income verification
- Credit scoring

### Approval Service (Port 8003)
- Contract PDF generation (reportlab)
- Amortization schedule generation
- Loan approval/rejection

### API Gateway (Port 8000)
- Single entry point for frontend
- Routes to appropriate microservice
- Health monitoring

## 📊 Database Schema

```sql
CREATE TABLE loan_applications (
    id SERIAL PRIMARY KEY,
    application_id VARCHAR(255) UNIQUE NOT NULL,
    amount DECIMAL(12, 2) NOT NULL,
    duration INTEGER NOT NULL,
    income DECIMAL(12, 2) NOT NULL,
    id_document VARCHAR(255),
    salary_slip VARCHAR(255),
    contract_path VARCHAR(255),
    amortization_path VARCHAR(255),
    extracted_income DECIMAL(12, 2),
    status VARCHAR(50) DEFAULT 'Submitted',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 🔧 Configuration

Environment variables (`.env`):
```env
DATABASE_URL=postgresql://postgres:1234@localhost:5432/loandb
APPLICATION_SERVICE_URL=http://localhost:8001
PROCESSING_SERVICE_URL=http://localhost:8002
APPROVAL_SERVICE_URL=http://localhost:8003
UPLOAD_DIR=uploads
```

## 📝 Status Flow

```
Submitted → Pre-approved → Approved
         ↘ Review-required ↗
         ↘ Rejected
```
