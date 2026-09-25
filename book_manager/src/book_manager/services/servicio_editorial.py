from ..entities.editorial import Editorial
from .servicio_base import ServicioBase


class ServicioEditorial(ServicioBase[Editorial]):
    """No tiene reglas extra: el nombre ya lo valida la entidad."""

    tipo = Editorial
