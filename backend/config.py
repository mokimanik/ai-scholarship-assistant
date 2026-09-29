import os
from pathlib import Path
from dotenv import load_dotenv

# Base project directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env file
load_dotenv(BASE_DIR / ".env")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    os.environ["GEMINI_API_KEY"] = GEMINI_API_KEY

# Application Configuration
APP_NAME = "AI Scholarship Assistant Backend"
VERSION = "1.0.0"

# Data file paths
EXCEL_FILE_PATH = BASE_DIR / "data" / "students_data.xlsx"
STUDENTS_FILE_PATH = BASE_DIR / "data" / "students.json"
SCHOLARSHIPS_FILE_PATH = BASE_DIR / "data" / "scholarships.json"
APPLICATIONS_FILE_PATH = BASE_DIR / "data" / "applications.json"

# Model Configurations
LLM_MODEL = "gemini-3.8-flash"
EMBEDDING_MODEL = "models/gemini-embedding-001"
CREW_LLM_MODEL = "gemini/gemini-3.8-flash"

# RAG paths
DOCS_DIR = BASE_DIR / "docs"
CHROMA_DB_DIR = BASE_DIR / "backend" / "rag" / "chroma_db"


