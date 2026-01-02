import os
from pathlib import Path
from dotenv import load_dotenv

# Base directory of the project (agenda-piloto/)
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env
load_dotenv(BASE_DIR / ".env")

# Google Sheets configuration
GOOGLE_CREDS_PATH = BASE_DIR / os.getenv("GOOGLE_CREDS_PATH", "credentials.json")
SHEET_ID = os.getenv("SHEET_ID")

# Default business values
DEFAULT_DURACION_MIN = 30
DEFAULT_FLEXIBILIDAD = "No"
DEFAULT_SERVICIO = "Servicio"
