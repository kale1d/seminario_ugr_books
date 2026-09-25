"""Clases base de las que heredan las demás entidades."""

from .validaciones import validar_texto


class EntidadBase:
    """Toda entidad que se guarda por ID hereda de acá."""

    def __init__(self, id: int) -> None:
        if not isinstance(id, int):
            raise TypeError("El ID debe ser un número entero.")
        if id <= 0:
            raise ValueError("El ID debe ser mayor a cero.")
        self.__id = id

    @property
    def id(self) -> int:
        return self.__id


class EntidadConNombre(EntidadBase):
    """Para las entidades que son básicamente un ID y un nombre
    (Genero, Editorial, TipoCotizacion y Moneda)."""

    def __init__(self, id: int, nombre: str) -> None:
        super().__init__(id)
        self.nombre = nombre

    @property
    def nombre(self) -> str:
        return self.__nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        self.__nombre = validar_texto(valor, "El nombre")

    def __str__(self) -> str:
        return self.nombre
