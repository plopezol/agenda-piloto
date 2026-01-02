import os
import json
from pathlib import Path
from typing import Optional, Tuple

import gspread
from google.oauth2.service_account import Credentials

from .settings import SHEET_ID


SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

# --- Credentials handling (local + Railway) ---
CREDS_PATH = Path(
    os.getenv("GOOGLE_CREDS_PATH", "/tmp/credentials.json")
)

_creds_json = os.getenv("GOOGLE_CREDENTIALS_JSON")

if _creds_json:
    try:
        CREDS_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(CREDS_PATH, "w") as f:
            json.dump(json.loads(_creds_json), f)
    except Exception as e:
        raise RuntimeError(f"❌ Error writing Google credentials from env: {e}")


def _get_client() -> gspread.Client:
    """
    Devuelve un cliente autenticado de gspread.
    Soporta credenciales locales o vía variable de entorno (Railway).
    """
    if not CREDS_PATH.exists():
        raise FileNotFoundError(
            f"❌ No se encuentra credentials.json en {CREDS_PATH}"
        )

    creds = Credentials.from_service_account_file(
        CREDS_PATH,
        scopes=SCOPES,
    )
    return gspread.authorize(creds)


def _get_spreadsheet():
    """
    Abre el spreadsheet principal por SHEET_ID.
    """
    if not SHEET_ID:
        raise ValueError("❌ SHEET_ID no definido en el .env")

    client = _get_client()
    return client.open_by_key(SHEET_ID)


def get_ws_dia(fecha_iso: Optional[str] = None) -> Tuple[gspread.Worksheet, str]:
    """
    Devuelve la worksheet correspondiente a una fecha.
    - Si fecha_iso es None → usa la fecha actual (YYYY-MM-DD)
    - Si la hoja no existe → la crea duplicando PLANTILLA_DIA
    """
    from datetime import date

    sh = _get_spreadsheet()

    if not fecha_iso:
        fecha_iso = date.today().isoformat()

    hojas = {ws.title: ws for ws in sh.worksheets()}

    if fecha_iso in hojas:
        return hojas[fecha_iso], fecha_iso

    # Crear desde plantilla
    if "PLANTILLA_DIA" not in hojas:
        raise ValueError("❌ No existe la hoja PLANTILLA_DIA")

    plantilla = hojas["PLANTILLA_DIA"]

    sh.duplicate_sheet(
        source_sheet_id=plantilla.id,
        new_sheet_name=fecha_iso,
    )

    ws_nueva = sh.worksheet(fecha_iso)
    return ws_nueva, fecha_iso
