from pydantic import BaseModel, Field
from typing import Optional


class EstadoUpdate(BaseModel):
    """
    Payload para cambiar el estado de una cita.
    """
    row_sheet: int = Field(
        ...,
        description="Número de fila en Google Sheet (row_sheet)"
    )
    estado: str = Field(
        ...,
        description="Nuevo estado: confirmada | cancelada | hueco"
    )


class CitaCreate(BaseModel):
    """
    Payload para crear o completar una cita.
    """
    fecha: Optional[str] = Field(
        default=None,
        description="Fecha en formato YYYY-MM-DD. Si es None, se usa hoy."
    )
    row_sheet: int = Field(
        ...,
        description="Número de fila en Google Sheet (row_sheet)"
    )
    cliente: str = Field(
        default="",
        description="Nombre del cliente"
    )
    telefono: str = Field(
        default="",
        description="Teléfono del cliente"
    )
    servicio: str = Field(
        default="",
        description="Servicio solicitado"
    )
    duracion: Optional[int] = Field(
        default=None,
        description="Duración del servicio en minutos"
    )
    flexibilidad: Optional[str] = Field(
        default=None,
        description="Flexibilidad del cliente: Si | No"
    )
