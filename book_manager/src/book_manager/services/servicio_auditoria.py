"""Auditoría: registro de las operaciones que se hacen en el sistema."""

import functools
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any, Callable, List

from ..entities.auditoria import Auditoria
from ..repositories.interfaces import IRepositorioAuditoria


class ServicioAuditoria:
    """Guarda y consulta el historial de operaciones del sistema."""

    def __init__(self, repositorio: IRepositorioAuditoria) -> None:
        """Guarda el repositorio de auditoría."""
        self._repositorio = repositorio

    def registrar(self, accion: str, detalles: str = "") -> Auditoria:
        """Guarda una operación en el historial con la fecha y hora actual.

        Args:
            accion (str): Nombre de la operación.
            detalles (str): Descripción de lo que se hizo.

        Returns:
            Auditoria: El registro guardado.

        Raises:
            ValueError: Si la acción está vacía.
        """
        if not isinstance(accion, str) or not accion.strip():
            raise ValueError("La acción a auditar no puede estar vacía.")
        return self._repositorio.crear(Auditoria(
            accion=accion.strip(), detalles=detalles, fecha=datetime.now(),
        ))

    def leer_historial(self) -> List[Auditoria]:
        """Devuelve el historial, del registro más nuevo al más viejo."""
        return self._repositorio.leer_todos()


def _describir(valor: Any) -> str:
    """Resume un argumento para el historial: los valores simples se
    muestran tal cual y los objetos con su clase y su identificador."""
    if valor is None or isinstance(
            valor, (str, int, float, Decimal, date, datetime)):
        return repr(valor)
    claves = [f"{atributo}={getattr(valor, atributo)}"
              for atributo in ("id", "libro_id", "tipo_id", "fecha")
              if hasattr(valor, atributo)]
    nombre = type(valor).__name__
    return f"{nombre}({', '.join(claves)})" if claves else nombre


def _describir_resultado(resultado: Any) -> str:
    """Resume lo que devolvió la operación (archivo generado o cantidad de
    registros), si es algo que vale la pena registrar."""
    ruta = resultado if isinstance(resultado, Path) else getattr(
        resultado, "ruta", None)
    if isinstance(ruta, Path):
        return f"archivo={ruta.name}"
    if isinstance(resultado, list):
        return f"{len(resultado)} registros"
    return ""


def auditar(accion: str) -> Callable:
    """Decorador que registra en el historial cada vez que se ejecuta un
    método de un servicio, y si terminó bien o con error.

    El servicio tiene que guardar su ServicioAuditoria en ``self._auditoria``.
    Si no tiene (es None), el método se ejecuta igual, sin registrar.

    Args:
        accion (str): Nombre con el que queda registrada la operación.

    Returns:
        Callable: El decorador.
    """
    def decorador(funcion: Callable) -> Callable:
        @functools.wraps(funcion)
        def envoltura(self, *args, **kwargs):
            auditoria = getattr(self, "_auditoria", None)
            argumentos = ", ".join(
                [_describir(a) for a in args]
                + [f"{k}={_describir(v)}" for k, v in kwargs.items()]
            )
            llamada = f"{type(self).__name__}.{funcion.__name__}({argumentos})"
            try:
                resultado = funcion(self, *args, **kwargs)
            except Exception as error:
                if auditoria is not None:
                    auditoria.registrar(accion, f"{llamada} - ERROR: {error}")
                raise
            if auditoria is not None:
                extra = _describir_resultado(resultado)
                auditoria.registrar(
                    accion, f"{llamada} - OK" + (f" ({extra})" if extra else "")
                )
            return resultado
        return envoltura
    return decorador
