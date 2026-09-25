from ..entities.genero import Genero
from .servicio_base import ServicioBase


class ServicioGenero(ServicioBase[Genero]):
    """No tiene reglas extra: el nombre ya lo valida la entidad."""

    tipo = Genero
