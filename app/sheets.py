import os
import json
from pathlib import Path
from typing import Optional, Tuple, List, Dict
from functools import lru_cache
from datetime import date

import gspread
from google.oauth2.service_account import Credentials

from .settings import SHEET_ID

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

# ---------------------------------------------------------------------
# Credentials (LOCAL + RAILWAY)
# ---------------------------------------------------------------------

# Railway: GOOGLE_CREDS_JSON (JSON completo)
# Local: credentials.json
GOOGLE_CREDS_JSON = os.getenv("GOOGLE_CREDS_JSON")
LOCAL_CREDS_PATH = Path("credentials.json")

def _load_credentials() -> Credentials:
    if GOOGLE_CREDS_JSON:
        info = json.loads(GOOGLE_CREDS_JSON)
        return Credentials.from_service_account_info(info, scopes=SCOPES)

    if LOCAL_CREDS_PATH.exists():
        return Credentials.from_service_account_file(
            LOCAL_CREDS_PATH, scopes=SCOPES
        )

    raise RuntimeError(
        "❌ No Google credentials found. "
        "Set GOOGLE_CREDS_JSON (Railway) or provide credentials.json (local)."
    )

# ---------------------------------------------------------------------
# Client & Spreadsheet (cached)
# ---------------------------------------------------------------------

@lru_cache(maxsize=1)
def get_client() -> gspread.Client:
    creds = _load_credentials()
    return gspread.authorize(creds)

@lru_cache(maxsize=1)
def get_spreadsheet() -> gspread.Spreadsheet:
    if not SHEET_ID:
        raise ValueError("❌ SHEET_ID no definido")
    return get_client().open_by_key(SHEET_ID)

# ---------------------------------------------------------------------
# Worksheets (one per day)
# ---------------------------------------------------------------------

EXPECTED_HEADERS = [
    "Hora",
    "Estado",
    "Cliente",
    "Teléfono",
    "Servicio",
    "Duración",
    "Flexibilidad",
    "Notas",
    "Avisada",
]

def get_ws_dia(fecha_iso: Optional[str] = None) -> Tuple[gspread.Worksheet, str]:
    """
    Devuelve la worksheet del día (YYYY-MM-DD).
    Si no existe, la crea duplicando PLANTILLA_DIA.
    """
    if not fecha_iso:
        fecha_iso = date.today().isoformat()

    sh = get_spreadsheet()
    hojas = {ws.title: ws for ws in sh.worksheets()}

    if fecha_iso in hojas:
        return hojas[fecha_iso], fecha_iso

    if "PLANTILLA_DIA" not in hojas:
        raise RuntimeError("❌ No existe la hoja PLANTILLA_DIA")

    plantilla = hojas["PLANTILLA_DIA"]

    sh.duplicate_sheet(
        source_sheet_id=plantilla.id,
        new_sheet_name=fecha_iso,
    )

    ws = sh.worksheet(fecha_iso)
    return ws, fecha_iso

# ---------------------------------------------------------------------
# Data helpers
# ---------------------------------------------------------------------

def read_agenda(ws: gspread.Worksheet) -> List[Dict]:
    """
    Lee la agenda del día de forma segura (sin errores de headers duplicados).
    """
    return ws.get_all_records(expected_headers=EXPECTED_HEADERS)

def update_cell(
    ws: gspread.Worksheet,
    row: int,
    column_name: str,
    value
) -> None:
    """
    Actualiza una celda por nombre de columna (1-based row).
    """
    headers = ws.row_values(1)
    if column_name not in headers:
        raise ValueError(f"❌ Columna '{column_name}' no existe")

    col_idx = headers.index(column_name) + 1
    ws.update_cell(row, col_idx, value)

def update_row(ws: gspread.Worksheet, row: int, data: Dict) -> None:
    """
    Actualiza múltiples columnas de una fila.
    """
    headers = ws.row_values(1)
    updates = []

    for key, value in data.items():
        if key in headers:
            col = headers.index(key) + 1
            updates.append((row, col, value))

    if updates:
        ws.batch_update([
            {
                "range": gspread.utils.rowcol_to_a1(r, c),
                "values": [[v]],
            }
            for r, c, v in updates
        ])
