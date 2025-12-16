# Loan Application Backend

FastAPI backend for loan application processing.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up PostgreSQL database:
```bash
# Create database
createdb loandb

# Or using psql
psql -U postgres
CREATE DATABASE loandb;
```

3. Configure environment variables:
```bash
# Copy .env.example to .env and update with your database credentials
cp .env.example .env
```

4. Run the server:
```bash
python main.py
# Or with uvicorn
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints

- `POST /api/loan-application` - Submit loan application with documents
- `GET /api/loan-applications` - Get all loan applications
- `GET /api/loan-application/{application_id}` - Get specific application

## Database Schema

```sql
CREATE TABLE loan_applications (
    id SERIAL PRIMARY KEY,
    application_id VARCHAR(255) UNIQUE NOT NULL,
    amount DECIMAL(12, 2) NOT NULL,
    duration INTEGER NOT NULL,
    income DECIMAL(12, 2) NOT NULL,
    id_document VARCHAR(255),
    salary_slip VARCHAR(255),
    status VARCHAR(50) DEFAULT 'Submitted',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```
