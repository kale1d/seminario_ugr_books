from decimal import Decimal

from .entidad_base import EntidadBase
from .libro import Libro
from .moneda import Moneda
from .validaciones import validar_importe, validar_tipo


class Precio(EntidadBase):
    """Lo que sale un libro en una moneda determinada."""

    def __init__(self, id: int, libro: Libro, moneda: Moneda, valor) -> None:
        super().__init__(id)
        # El libro y la moneda no se cambian: si cambia la moneda es otro precio
        self.__libro = validar_tipo(libro, Libro, "El libro")
        self.__moneda = validar_tipo(moneda, Moneda, "La moneda")
        self.valor = valor

    @property
    def libro(self) -> Libro:
        return self.__libro

    @property
    def moneda(self) -> Moneda:
        return self.__moneda

    @property
    def valor(self) -> Decimal:
        return self.__valor

    @valor.setter
    def valor(self, nuevo_valor) -> None:
        self.__valor = validar_importe(nuevo_valor)

    def __str__(self) -> str:
        return f"{self.libro.titulo}: {self.moneda.codigo} {self.valor}"
