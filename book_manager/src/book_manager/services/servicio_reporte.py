"""Generación del reporte de precios en Excel."""

from datetime import datetime
from pathlib import Path
from typing import Optional

import pandas as pd

from .servicio_auditoria import ServicioAuditoria, auditar
from .servicio_comparacion import CARPETA_REPORTES, ServicioComparacion

COLUMNAS = [
    "Libro", "Precio interno", "Precio web", "Diferencia",
    "Fecha de extracción",
]


def _a_numero(valor):
    """Convierte un Decimal en float para el Excel (None queda vacío)."""
    return None if valor is None else float(valor)


class ServicioReporte:
    """Genera el reporte en Excel que compara los precios propios con los
    de la web."""

    def __init__(self, comparacion: ServicioComparacion,
                 carpeta_reportes: Path = CARPETA_REPORTES,
                 auditoria: Optional[ServicioAuditoria] = None) -> None:
        """Guarda el servicio de comparación y la carpeta de destino.

        Args:
            comparacion (ServicioComparacion): Servicio que compara los
                precios de cada libro con los de la web.
            carpeta_reportes (Path): Carpeta donde se guarda el Excel.
            auditoria (Optional[ServicioAuditoria]): Servicio donde se
                registran las operaciones.
        """
        self._comparacion = comparacion
        self._carpeta = Path(carpeta_reportes)
        self._auditoria = auditoria

    @auditar("Generar reporte Excel")
    def generar_excel(self) -> Path:
        """Genera el Excel con una fila por libro del catálogo.

        Los libros que no se encontraron en la web quedan con el precio
        web, la diferencia y la fecha de extracción vacíos.

        Returns:
            Path: Ruta del archivo generado.
        """
        filas = [
            {
                "Libro": c.libro,
                "Precio interno": _a_numero(c.precio_interno),
                "Precio web": _a_numero(c.precio_web),
                "Diferencia": _a_numero(c.diferencia),
                "Fecha de extracción": c.fecha_extraccion,
            }
            for c in self._comparacion.comparar()
        ]
        tabla = pd.DataFrame(filas, columns=COLUMNAS)
        tabla["Fecha de extracción"] = pd.to_datetime(
            tabla["Fecha de extracción"]
        )

        self._carpeta.mkdir(parents=True, exist_ok=True)
        ruta = self._carpeta / f"reporte_precios_{datetime.now():%Y%m%d_%H%M%S}.xlsx"
        with pd.ExcelWriter(ruta, engine="openpyxl",
                            datetime_format="yyyy-mm-dd hh:mm") as escritor:
            tabla.to_excel(escritor, index=False, sheet_name="Precios")
            hoja = escritor.sheets["Precios"]
            for columna in hoja.columns:
                largo = max(len(str(celda.value or "")) for celda in columna)
                hoja.column_dimensions[columna[0].column_letter].width = (
                    max(largo + 2, 16)
                )
        return ruta