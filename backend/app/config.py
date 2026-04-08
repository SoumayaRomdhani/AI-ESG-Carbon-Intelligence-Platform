from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
KNOWLEDGE_DIR = DATA_DIR / "knowledge_base"
ARTIFACTS_DIR = BASE_DIR / "models_artifacts"
REPORTS_DIR = BASE_DIR / "generated_reports"

APP_NAME = os.getenv("APP_NAME", "CarbonLens")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./carbonlens.db")

for path in [DATA_DIR, RAW_DIR, PROCESSED_DIR, KNOWLEDGE_DIR, ARTIFACTS_DIR, REPORTS_DIR]:
    path.mkdir(parents=True, exist_ok=True)
