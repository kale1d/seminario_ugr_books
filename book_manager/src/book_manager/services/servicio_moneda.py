from ..entities.moneda import Moneda
from .servicio_base import ServicioBase


class ServicioMoneda(ServicioBase[Moneda]):
    """No puede haber dos monedas con el mismo código."""

    tipo = Moneda

    def _validar(self, entidad: Moneda) -> None:
        super()._validar(entidad)
        for moneda in self._repositorio.leer_todos():
            if moneda.id != entidad.id and moneda.codigo == entidad.codigo:
                raise ValueError(
                    f"Ya existe una moneda con código {entidad.codigo}."
                )
