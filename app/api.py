from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from .models import EstadoUpdate, CitaCreate
from .sheets import get_ws_dia
from .services import (
    leer_agenda,
    cambiar_estado,
    crear_cita,
    detectar_huecos,
    cambiar_avisada,
    mover_cita,
    sugerir_clientas_para_hueco,
)

router = APIRouter()


@router.get("/agenda")
def obtener_agenda(fecha: Optional[str] = Query(None, description="Fecha YYYY-MM-DD")):
    """
    Devuelve la agenda completa de un día.
    Si la hoja no existe, se crea automáticamente desde PLANTILLA_DIA.
    """
    try:
        ws, _ = get_ws_dia(fecha)
        agenda = leer_agenda(ws)
        return agenda
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/agenda/estado")
def actualizar_estado(
    payload: EstadoUpdate,
    fecha: Optional[str] = Query(None, description="Fecha YYYY-MM-DD"),
):
    """
    Cambia el estado de una cita (confirmada / cancelada / hueco)
    """
    try:
        ws, _ = get_ws_dia(fecha)
        cambiar_estado(
            ws=ws,
            row_sheet=payload.row_sheet,
            estado=payload.estado,
        )
        return {"ok": True}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/agenda/cita")
def crear_cita_endpoint(payload: CitaCreate):
    """
    Crea o completa una cita en una fila (normalmente un hueco).
    """
    try:
        ws, _ = get_ws_dia(payload.fecha)
        crear_cita(
            ws=ws,
            row_sheet=payload.row_sheet,
            cliente=payload.cliente,
            telefono=payload.telefono,
            servicio=payload.servicio,
            duracion=payload.duracion,
            flexibilidad=payload.flexibilidad,
        )
        return {"ok": True}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/agenda/huecos")
def obtener_huecos(fecha: Optional[str] = Query(None, description="Fecha YYYY-MM-DD")):
    """
    Detecta huecos y devuelve sugerencias de relleno.
    """
    try:
        ws, _ = get_ws_dia(fecha)
        huecos = detectar_huecos(ws)
        return huecos
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/agenda/avisada")
def actualizar_avisada(
    row_sheet: int,
    avisada: str,
    fecha: Optional[str] = Query(None, description="Fecha YYYY-MM-DD"),
):
    """
    Marca una cita como avisada (Si / No)
    """
    try:
        ws, _ = get_ws_dia(fecha)
        cambiar_avisada(
            ws=ws,
            row_sheet=row_sheet,
            avisada=avisada,
        )
        return {"ok": True}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/agenda/mover")
def mover_cita_endpoint(
    row_origen: int,
    row_destino: int,
    fecha: Optional[str] = Query(None, description="Fecha YYYY-MM-DD"),
):
    """
    Mueve una cita de una hora a otra (fila origen → fila destino)
    """
    try:
        ws, _ = get_ws_dia(fecha)
        mover_cita(
            ws=ws,
            row_origen=row_origen,
            row_destino=row_destino,
        )
        return {"ok": True}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
@router.get("/agenda/hueco/sugeridas")
def obtener_sugeridas_para_hueco(
    row_sheet: int,
    fecha: Optional[str] = Query(None, description="Fecha YYYY-MM-DD"),
):
    """
    Devuelve las clientas flexibles que encajan en un hueco concreto.
    """
    try:
        ws, _ = get_ws_dia(fecha)
        agenda = leer_agenda(ws)

        # Detectar huecos reales
        huecos = detectar_huecos(ws)
        hueco = next((h for h in huecos if h["row_sheet"] == row_sheet), None)

        if not hueco:
            return []

        return sugerir_clientas_para_hueco(
            agenda=agenda,
            duracion_hueco=hueco["Duracion"],
        )

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))