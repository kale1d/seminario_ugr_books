from sqlite3 import Row

from ..entities.precio import Precio
from .base_de_datos import BaseDeDatos
from .repositorio_base import RepositorioBase
from .repositorio_libro import RepositorioLibro
from .repositorio_moneda import RepositorioMoneda


class RepositorioPrecio(RepositorioBase[Precio]):
    """El valor se guarda como texto para no perder precisión del
    Decimal."""

    tabla = "precios"
    columnas = ("libro_id", "moneda_id", "valor")
    tipo = Precio

    def __init__(self, base: BaseDeDatos) -> None:
        super().__init__(base)
        self._libros = RepositorioLibro(base)
        self._monedas = RepositorioMoneda(base)

    def _a_fila(self, entidad: Precio) -> tuple:
        return (entidad.libro.id, entidad.moneda.id, str(entidad.valor))

    def _desde_fila(self, fila: Row) -> Precio:
        libro = self._libros.leer_por_id(fila["libro_id"])
        moneda = self._monedas.leer_por_id(fila["moneda_id"])
        if libro is None or moneda is None:
            raise ValueError(f"El precio {fila['id']} tiene datos rotos.")
        return Precio(fila["id"], libro, moneda, fila["valor"])
