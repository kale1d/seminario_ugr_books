"""Registro de auditoría: una operación realizada en el sistema."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class Auditoria:
    """Una acción registrada en el historial de auditoría.

    Attributes:
        accion: Nombre de la operación (por ejemplo, "Crear").
        detalles: Descripción de lo que se hizo y de cómo terminó.
        fecha: Fecha y hora en que se hizo.
        id: Identificador asignado por la base de datos al guardarlo.
    """

    accion: str
    detalles: str
    fecha: datetime
    id: Optional[int] = None
