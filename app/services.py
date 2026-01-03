from typing import List, Dict, Any
import re
import pandas as pd

from .settings import (
    DEFAULT_DURACION_MIN,
    DEFAULT_FLEXIBILIDAD,
    DEFAULT_SERVICIO,
)

# Columnas fijas (por claridad):
# A Hora
# B Estado
# C Cliente
# D Teléfono
# E Servicio
# F Duración
# G Flexibilidad
# H Notas
# I Avisada


# -------------------------
# Helpers de normalización
# -------------------------

def normaliza_estado(valor: str) -> str:
    if not valor:
        return "hueco"
    v = str(valor).strip().lower()
    if v in ("confirmada", "confirmado"):
        return "confirmada"
    if v in ("cancelada", "cancelado"):
        return "cancelada"
    if v in ("hueco", "vacío", "vacio"):
        return "hueco"
    return "hueco"


def duracion_a_minutos(valor) -> int:
    try:
        if valor is None or valor == "":
            return DEFAULT_DURACION_MIN
        return int(valor)
    except Exception:
        return DEFAULT_DURACION_MIN


def hora_a_minutos(hora: str) -> int:
    if not hora:
        return -1
    if isinstance(hora, (int, float)):
        return int(hora)
    m = re.match(r"^(\d{1,2}):(\d{2})$", str(hora))
    if not m:
        return -1
    return int(m.group(1)) * 60 + int(m.group(2))


# -------------------------
# Lectura de agenda
# -------------------------

def leer_agenda(ws) -> List[Dict[str, Any]]:
    """
    Lee todas las filas de la hoja (excepto cabecera)
    y devuelve una lista de dicts normalizados.
    """
    values = ws.get_all_values()
    if not values or len(values) < 2:
        return []

    filas: List[Dict[str, Any]] = []
    for idx, row in enumerate(values[1:], start=2):
        hora = row[0] if len(row) > 0 else ""
        estado_raw = row[1] if len(row) > 1 else ""
        cliente = row[2] if len(row) > 2 else ""
        telefono = row[3] if len(row) > 3 else ""
        servicio = row[4] if len(row) > 4 else ""
        duracion_raw = row[5] if len(row) > 5 else ""
        flex = row[6] if len(row) > 6 else ""
        avisada = row[8] if len(row) > 8 else ""

        estado = normaliza_estado(estado_raw)
        duracion = duracion_a_minutos(duracion_raw)
        servicio = servicio if servicio else DEFAULT_SERVICIO
        flex = flex if flex in ("Si", "No") else DEFAULT_FLEXIBILIDAD

        filas.append({
            "row_sheet": idx,
            "Hora": hora,
            "Hora_min": hora_a_minutos(hora),
            "Estado": estado,
            "Cliente": cliente,
            "Telefono": telefono,      # OJO: en frontend usamos row.Telefono
            "Servicio": servicio,
            "Duración": duracion,      # clave "Duración" como venías usando
            "Flexibilidad": flex,
            "Avisada": avisada,
        })

    return filas


# -------------------------
# Acciones de negocio
# -------------------------

def cambiar_estado(ws, row_sheet: int, estado: str) -> None:
    """
    Cambia el estado de una fila concreta.
    """
    estado_norm = normaliza_estado(estado)
    ws.update_cell(row_sheet, 2, estado_norm)


def crear_cita(
    ws,
    row_sheet: int,
    cliente: str = "",
    telefono: str = "",
    servicio: str = "",
    duracion: int | None = None,
    flexibilidad: str | None = None,
) -> None:
    """
    Crea o edita una cita en una fila.
    - Si la fila estaba en hueco → pasa a confirmada
    - Si ya estaba confirmada o cancelada → mantiene el estado
    """
    servicio = servicio if servicio else DEFAULT_SERVICIO
    duracion = int(duracion) if duracion not in (None, "") else DEFAULT_DURACION_MIN
    flexibilidad = flexibilidad if flexibilidad in ("Si", "No") else DEFAULT_FLEXIBILIDAD

    # Leer estado actual (col B)
    estado_actual = ws.cell(row_sheet, 2).value
    estado_actual = normaliza_estado(estado_actual)

    # Solo forzar confirmada si era hueco
    if estado_actual == "hueco":
        ws.update_cell(row_sheet, 2, "confirmada")

    # Actualizar datos (C..G)
    ws.update_cell(row_sheet, 3, cliente)
    ws.update_cell(row_sheet, 4, telefono)
    ws.update_cell(row_sheet, 5, servicio)
    ws.update_cell(row_sheet, 6, duracion)
    ws.update_cell(row_sheet, 7, flexibilidad)


# -------------------------
# Detección de huecos
# -------------------------

def detectar_huecos(ws) -> List[Dict[str, Any]]:
    """
    Detecta huecos reales teniendo en cuenta:
    - Hora de inicio
    - Siguiente cita
    - Duración real disponible
    - Si el hueco permite servicios largos
    """
    agenda = leer_agenda(ws)
    if not agenda:
        return []

    df = pd.DataFrame(agenda)
    df = df.sort_values("Hora_min")

    huecos: List[Dict[str, Any]] = []

    for idx, row in df.iterrows():
        if row["Estado"] != "hueco":
            continue

        inicio = int(row["Hora_min"])
        row_sheet = int(row["row_sheet"])

        # Buscar siguiente cita confirmada (ignorar otros huecos)
        siguientes = df[
            (df["Hora_min"] > inicio) &
            (df["Estado"] != "hueco")
        ]

        if not siguientes.empty:
            siguiente = siguientes.iloc[0]
            fin = int(siguiente["Hora_min"])
            duracion_real = max(0, fin - inicio)
        else:
            # Si no hay siguiente cita, dejamos un máximo razonable (ej. 180 min)
            duracion_real = 180

        # Determinar si admite servicios largos
        admite_largo = duracion_real >= 60

        huecos.append({
            "Hora": row["Hora"],
            "Hora_min": inicio,
            "Duracion": duracion_real,
            "row_sheet": row_sheet,
            "Admite_largo": admite_largo,
        })

    return huecos

def cambiar_avisada(ws, row_sheet: int, avisada: str) -> None:
    """
    Marca una cita como avisada o no avisada.
    Columna I (Avisada): valores esperados 'Si' o 'No'
    """
    valor = avisada if avisada in ("Si", "No") else "No"
    ws.update_cell(row_sheet, 9, valor)

def mover_cita(ws, row_origen: int, row_destino: int) -> None:
    """
    Mueve una cita de una fila a otra.
    - La fila destino debe estar en estado HUECO
    - Copia todos los datos de la cita
    - Limpia la fila origen y la deja como HUECO
    """

    # Leer estado destino
    estado_destino = normaliza_estado(ws.cell(row_destino, 2).value)
    if estado_destino != "hueco":
        raise ValueError("La fila destino no está libre")

    # Leer datos de origen
    estado_origen = normaliza_estado(ws.cell(row_origen, 2).value)
    if estado_origen == "hueco":
        raise ValueError("No se puede mover un hueco")

    cliente = ws.cell(row_origen, 3).value or ""
    telefono = ws.cell(row_origen, 4).value or ""
    servicio = ws.cell(row_origen, 5).value or DEFAULT_SERVICIO
    duracion = ws.cell(row_origen, 6).value or DEFAULT_DURACION_MIN
    flexibilidad = ws.cell(row_origen, 7).value or DEFAULT_FLEXIBILIDAD
    avisada = ws.cell(row_origen, 9).value or "No"

    # Escribir en destino
    ws.update_cell(row_destino, 2, "confirmada")
    ws.update_cell(row_destino, 3, cliente)
    ws.update_cell(row_destino, 4, telefono)
    ws.update_cell(row_destino, 5, servicio)
    ws.update_cell(row_destino, 6, duracion)
    ws.update_cell(row_destino, 7, flexibilidad)
    ws.update_cell(row_destino, 9, avisada)

    # Limpiar origen (dejar como hueco)
    ws.update_cell(row_origen, 2, "hueco")
    ws.update_cell(row_origen, 3, "")
    ws.update_cell(row_origen, 4, "")
    ws.update_cell(row_origen, 5, DEFAULT_SERVICIO)
    ws.update_cell(row_origen, 6, DEFAULT_DURACION_MIN)
    ws.update_cell(row_origen, 7, DEFAULT_FLEXIBILIDAD)
    ws.update_cell(row_origen, 9, "No")
def sugerir_clientas_para_hueco(
    agenda: List[Dict[str, Any]],
    duracion_hueco: int
) -> List[Dict[str, Any]]:
    """
    Devuelve clientas compatibles con un hueco:
    - Flexibilidad = Si
    - Duración del servicio <= duración del hueco
    - No avisadas
    """
    sugeridas = []

    for row in agenda:
        if row["Estado"] != "confirmada":
            continue
        if row["Flexibilidad"] != "Si":
            continue
        if row["Avisada"] == "Si":
            continue
        if row["Duración"] > duracion_hueco:
            continue

        sugeridas.append({
            "Cliente": row["Cliente"],
            "Telefono": row["Telefono"],
            "Servicio": row["Servicio"],
            "Duración": row["Duración"],
            "row_sheet": row["row_sheet"],
        })

    return sugeridas


# -------------------------
# Detección de retrasos y adelantos (FASE 1)
# -------------------------

def detectar_retrasos_y_adelantos(
    ws,
    margen_adelanto: int = 5
) -> List[Dict[str, Any]]:
    """
    Detecta conflictos de tiempo en la agenda:
    - Retrasos: una cita se come a la siguiente
    - Adelantos: hay hueco suficiente antes de la siguiente cita
    Devuelve una lista de avisos (no ejecuta acciones).
    """
    agenda = leer_agenda(ws)
    if not agenda:
        return []

    df = pd.DataFrame(agenda)
    df = df.sort_values("Hora_min")

    avisos: List[Dict[str, Any]] = []

    for i in range(len(df) - 1):
        actual = df.iloc[i]
        siguiente = df.iloc[i + 1]

        # Solo analizamos citas confirmadas
        if actual["Estado"] != "confirmada":
            continue
        if siguiente["Estado"] != "confirmada":
            continue

        inicio_actual = actual["Hora_min"]
        duracion_actual = actual["Duración"]
        fin_previsto = inicio_actual + duracion_actual

        inicio_siguiente = siguiente["Hora_min"]

        # Caso 1: Retraso
        if fin_previsto > inicio_siguiente:
            retraso = fin_previsto - inicio_siguiente
            avisos.append({
                "tipo": "retraso",
                "minutos": retraso,
                "afecta_a": {
                    "Cliente": siguiente["Cliente"],
                    "Telefono": siguiente["Telefono"],
                    "row_sheet": siguiente["row_sheet"],
                },
                "causado_por": {
                    "Cliente": actual["Cliente"],
                    "Servicio": actual["Servicio"],
                    "row_sheet": actual["row_sheet"],
                }
            })

        # Caso 2: Adelanto posible
        hueco = inicio_siguiente - fin_previsto
        if hueco >= margen_adelanto:
            avisos.append({
                "tipo": "adelanto",
                "minutos": hueco,
                "posible_con": {
                    "Cliente": siguiente["Cliente"],
                    "Telefono": siguiente["Telefono"],
                    "row_sheet": siguiente["row_sheet"],
                },
                "libre_desde": fin_previsto,
            })

    return avisos


def aplicar_retraso_manual(
    ws,
    row_sheet: int,
    minutos: int
) -> None:
    """
    Aplica un retraso manual sumando minutos a la hora de una cita.
    No reordena filas, solo ajusta la hora.
    """
    hora_actual = ws.cell(row_sheet, 1).value
    hora_min = hora_a_minutos(hora_actual)

    if hora_min < 0:
        raise ValueError("Hora inválida")

    nueva_hora = hora_min + minutos
    horas = nueva_hora // 60
    mins = nueva_hora % 60
    hora_txt = f"{horas:02d}:{mins:02d}"

    ws.update_cell(row_sheet, 1, hora_txt)
    

# -------------------------
# Mensajes WhatsApp (FASE 1)
# -------------------------

def mensaje_hueco(
    cliente: str,
    fecha: str,
    hora: str,
    servicio: str
) -> str:
    """
    Mensaje estándar para avisar de hueco libre.
    No envía nada, solo devuelve el texto.
    """
    return (
        f"Hola {cliente} 😊\n"
        f"Se ha quedado un hueco libre el {fecha} a las {hora} "
        f"para {servicio}.\n"
        f"¿Te vendría bien?"
    )

def marcar_clientas_avisadas(ws, rows_sheet: list[int]) -> None:
    """
    Marca como 'Avisada = Si' varias filas de la agenda.
    Se usa después de intentar avisar por WhatsApp.
    """
    for row in rows_sheet:
        ws.update_cell(row, 9, "Si")