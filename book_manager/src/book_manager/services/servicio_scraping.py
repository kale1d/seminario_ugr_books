"""Ejecución del scraper de Cúspide y generación de alertas de precio."""

import os
import subprocess
import sys
from decimal import Decimal
from pathlib import Path
from typing import Optional

from .servicio_auditoria import ServicioAuditoria, auditar
from .servicio_comparacion import ResultadoAlertas, ServicioComparacion

# Carpeta "src", necesaria para que el subproceso encuentre el paquete.
CARPETA_SRC = Path(__file__).resolve().parents[2]


class ServicioScraping:
    """Lanza el scraper y, al terminar, genera el CSV de alertas."""

    def __init__(self, comparacion: ServicioComparacion,
                 auditoria: Optional[ServicioAuditoria] = None) -> None:
        """Guarda el servicio de comparación.

        Args:
            comparacion (ServicioComparacion): Servicio que compara los
                precios y genera las alertas.
            auditoria (Optional[ServicioAuditoria]): Servicio donde se
                registran las operaciones.
        """
        self._comparacion = comparacion
        self._auditoria = auditoria

    @auditar("Ejecutar scraping")
    def ejecutar(self, umbral: Decimal,
                 libro_id: Optional[int] = None) -> ResultadoAlertas:
        """Ejecuta el scraper y genera las alertas de precio.

        Args:
            umbral (Decimal): Diferencia porcentual mínima para alertar.
            libro_id (Optional[int]): Si se indica, solo se scrapea ese
                libro; si no, todo el catálogo.

        Returns:
            ResultadoAlertas: Archivo CSV generado y totales.

        Raises:
            ValueError: Si el umbral es negativo.
            RuntimeError: Si el scraper terminó con error.
        """
        if umbral < 0:
            raise ValueError("La diferencia mínima no puede ser negativa.")

        comando = [sys.executable, "-m", "book_manager.scraper.runner"]
        if libro_id is not None:
            comando.append(str(libro_id))
        entorno = {**os.environ, "PYTHONPATH": str(CARPETA_SRC)}

        resultado = subprocess.run(
            comando, env=entorno, cwd=CARPETA_SRC.parent
        )
        if resultado.returncode != 0:
            raise RuntimeError(
                "El scraper terminó con error "
                f"(código {resultado.returncode})."
            )
        return self._comparacion.generar_alertas(umbral)