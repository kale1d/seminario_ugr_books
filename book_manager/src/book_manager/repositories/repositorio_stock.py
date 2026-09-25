from sqlite3 import Row
from typing import List, Optional

from ..entities.stock import Stock
from .base_de_datos import BaseDeDatos
from .interfaces import IRepositorioStock
from .repositorio_libro import RepositorioLibro


class RepositorioStock(IRepositorioStock):
    """Guarda un registro de stock por libro."""

    def __init__(self, base: BaseDeDatos) -> None:
        self._base = base
        self._libros = RepositorioLibro(base)

    def crear(self, stock: Stock) -> Stock:
        self._validar_tipo(stock)
        self._base.ejecutar(
            "INSERT INTO stock (libro_id, cantidad) VALUES (?, ?)",
            (stock.libro_id, stock.cantidad),
        )
        return stock

    def leer_por_libro(self, libro_id: int) -> Optional[Stock]:
        filas = self._base.consultar(
            "SELECT * FROM stock WHERE libro_id = ?", (libro_id,)
        )
        if not filas:
            return None
        return self._desde_fila(filas[0])

    def leer_todos(self) -> List[Stock]:
        filas = self._base.consultar("SELECT * FROM stock ORDER BY libro_id")
        return [self._desde_fila(fila) for fila in filas]

    def actualizar(self, stock: Stock) -> Stock:
        self._validar_tipo(stock)
        modificadas = self._base.ejecutar(
            "UPDATE stock SET cantidad = ? WHERE libro_id = ?",
            (stock.cantidad, stock.libro_id),
        )
        if modificadas == 0:
            raise ValueError("No hay stock cargado para ese libro.")
        return stock

    def eliminar(self, libro_id: int) -> bool:
        borradas = self._base.ejecutar(
            "DELETE FROM stock WHERE libro_id = ?", (libro_id,)
        )
        return borradas > 0

    def _validar_tipo(self, stock: Stock) -> None:
        if not isinstance(stock, Stock):
            raise TypeError("Se esperaba un objeto Stock.")

    def _desde_fila(self, fila: Row) -> Stock:
        libro = self._libros.leer_por_id(fila["libro_id"])
        if libro is None:
            raise ValueError(f"El stock del libro {fila['libro_id']} "
                             "apunta a un libro que no existe.")
        return Stock(libro, fila["cantidad"])
