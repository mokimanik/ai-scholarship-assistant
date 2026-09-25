from pathlib import Path

# Base project directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Application Configuration
APP_NAME = "AI Scholarship Assistant Backend"
VERSION = "1.0.0"

# Data file paths
EXCEL_FILE_PATH = BASE_DIR / "data" / "students_data.xlsx"
STUDENTS_FILE_PATH = BASE_DIR / "data" / "students.json"
SCHOLARSHIPS_FILE_PATH = BASE_DIR / "data" / "scholarships.json"
APPLICATIONS_FILE_PATH = BASE_DIR / "data" / "applications.json"

# Model Configurations
RAG_LLM_MODEL = "llama3.1"
CREW_LLM_MODEL = "ollama/llama3.1"
OLLAMA_BASE_URL = "http://localhost:11434"

# RAG paths
DOCS_DIR = BASE_DIR / "docs"
CHROMA_DB_DIR = BASE_DIR / "backend" / "rag" / "chroma_db"

