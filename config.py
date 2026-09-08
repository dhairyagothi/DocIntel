import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
UPLOAD_DIR = DATA_DIR / "uploads"
PROCESSED_DIR = DATA_DIR / "processed"
DATABASE_DIR = BASE_DIR / "database"
DATABASE_PATH = DATABASE_DIR / "docintel.db"

for directory in (UPLOAD_DIR, PROCESSED_DIR, DATABASE_DIR):
    directory.mkdir(parents=True, exist_ok=True)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
MAX_CHUNK_CHARS = int(os.getenv("MAX_CHUNK_CHARS", "8000"))
MATCH_THRESHOLD = float(os.getenv("MATCH_THRESHOLD", "0.80"))
FACT_CONFIDENCE_THRESHOLD = float(os.getenv("FACT_CONFIDENCE_THRESHOLD", "0.60"))
APP_VERSION = "0.1.0"