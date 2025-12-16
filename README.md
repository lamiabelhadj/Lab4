# Loan Application System

A full-stack loan application system built with React frontend and FastAPI backend.

## Features

- 📝 Loan application form (amount, duration, income)
- 📄 PDF document upload (ID, salary slip)
- 💾 PostgreSQL database storage
- 📁 Local file storage for documents
- ✅ Application status tracking

## Tech Stack

### Frontend
- React 18 with TypeScript
- Vite (build tool)
- Custom CSS styling

### Backend
- FastAPI (Python)
- PostgreSQL with asyncpg
- Pydantic for validation

## Getting Started

### Prerequisites
- Node.js 18+
- Python 3.10+
- PostgreSQL

### Backend Setup

1. Navigate to backend:
```bash
cd backend
```

2. Create virtual environment:
```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create PostgreSQL database:
```sql
CREATE DATABASE loandb;
```

5. Run the server:
```bash
python main.py
```

Backend runs at http://localhost:8000

### Frontend Setup

1. Navigate to frontend:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Run development server:
```bash
npm run dev
```

Frontend runs at http://localhost:5173

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/loan-application | Submit new loan application |
| GET | /api/loan-applications | Get all applications |
| GET | /api/loan-application/{id} | Get specific application |

## Project Structure

```
Lab4/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── requirements.txt     # Python dependencies
│   ├── README.md
│   └── uploads/             # Document storage
├── frontend/
│   ├── src/
│   │   ├── App.tsx          # Main application
│   │   ├── App.css          # Styles
│   │   └── main.tsx         # Entry point
│   ├── package.json
│   └── vite.config.ts
└── README.md
```

## Usage

1. Start the backend server
2. Start the frontend development server
3. Open http://localhost:5173 in your browser
4. Fill in the loan application form
5. Upload required PDF documents
6. Submit the application
7. Receive confirmation with application ID
