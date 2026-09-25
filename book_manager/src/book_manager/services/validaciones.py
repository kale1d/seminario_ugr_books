"""Validaciones que usan varios servicios."""

from typing import TypeVar

from ..entities.entidad_base import EntidadBase
from ..repositories.interfaces import IRepositorio

T = TypeVar("T", bound=EntidadBase)


def exigir_existente(repo: IRepositorio[T], id: int, nombre: str) -> T:
    """Busca la entidad por ID y lanza ValueError si no existe.

    Sirve para dar un mensaje claro que diga qué es lo que falta.
    """
    entidad = repo.leer_por_id(id)
    if entidad is None:
        raise ValueError(f"No existe {nombre} con ID {id}.")
    return entidad
