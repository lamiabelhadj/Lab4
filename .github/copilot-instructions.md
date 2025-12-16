<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# Loan Application System

This is a full-stack loan application system with:

## Frontend (React + TypeScript + Vite)
- Located in `/frontend`
- Uses React with TypeScript
- Styled with custom CSS
- Form handling with React hooks
- File upload for PDF documents

## Backend (FastAPI + Python)
- Located in `/backend`
- RESTful API endpoints
- PostgreSQL database with asyncpg
- File storage in local volume
- CORS enabled for frontend communication

## Key Technologies
- React 18 with TypeScript
- FastAPI with Pydantic
- PostgreSQL database
- Local file storage for documents

## API Endpoints
- POST /api/loan-application - Submit loan application
- GET /api/loan-applications - Get all applications
- GET /api/loan-application/{id} - Get specific application
