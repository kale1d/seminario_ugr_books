from decimal import Decimal
from typing import Union

from .entidad_base import EntidadBase
from .libro import Libro
from .moneda import Moneda
from .validaciones import validar_importe, validar_tipo


class Precio(EntidadBase):
    """Lo que sale un libro en una moneda determinada.

    El libro y la moneda no se pueden cambiar: si cambia la moneda,
    es otro precio.
    """

    def __init__(self, id: int, libro: Libro, moneda: Moneda,
                 valor: Union[Decimal, int, float, str]) -> None:
        super().__init__(id)
        validar_tipo(libro, Libro, "El libro")
        validar_tipo(moneda, Moneda, "La moneda")
        self.__libro = libro
        self.__moneda = moneda
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
    def valor(self, nuevo_valor: Union[Decimal, int, float, str]) -> None:
        self.__valor = validar_importe(nuevo_valor)

    def __str__(self) -> str:
        return f"{self.libro.titulo}: {self.moneda.codigo} {self.valor}"
