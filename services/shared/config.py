import os
from dotenv import load_dotenv

load_dotenv()

# Database configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:1234@localhost:5432/loandb"
)

# Service URLs
APPLICATION_SERVICE_URL = os.getenv("APPLICATION_SERVICE_URL", "http://localhost:8001")
PROCESSING_SERVICE_URL = os.getenv("PROCESSING_SERVICE_URL", "http://localhost:8002")
APPROVAL_SERVICE_URL = os.getenv("APPROVAL_SERVICE_URL", "http://localhost:8003")

# Upload directory
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
