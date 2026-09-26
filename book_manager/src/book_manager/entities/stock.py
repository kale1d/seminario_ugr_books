from .libro import Libro
from .validaciones import validar_tipo


class Stock:
    """Unidades disponibles de un libro.

    No tiene ID propio, se identifica por el libro.
    """

    def __init__(self, libro: Libro, cantidad: int = 0) -> None:
        validar_tipo(libro, Libro, "El libro")
        self.__libro = libro
        self.cantidad = cantidad

    @property
    def libro(self) -> Libro:
        return self.__libro

    @property
    def libro_id(self) -> int:
        """ID del libro, que es lo que usa el repositorio para buscar."""
        return self.__libro.id

    @property
    def cantidad(self) -> int:
        return self.__cantidad

    @cantidad.setter
    def cantidad(self, valor: int) -> None:
        if not isinstance(valor, int):
            raise TypeError("La cantidad debe ser un número entero.")
        if valor < 0:
            raise ValueError("La cantidad no puede ser negativa.")
        self.__cantidad = valor

    def __str__(self) -> str:
        return f"{self.libro.titulo}: {self.cantidad} unidades"
