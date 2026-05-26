from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent.parent

APP_ENV = os.getenv("APP_ENV", "development")

DATA_PATH = os.getenv(
    "DATA_PATH",
    str(BASE_DIR / "data" / "processed" / "race_results_clean.csv")
)