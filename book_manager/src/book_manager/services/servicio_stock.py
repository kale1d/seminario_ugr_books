from typing import List, Optional

from ..entities.libro import Libro
from ..entities.stock import Stock
from ..repositories.interfaces import IRepositorio, IRepositorioStock
from .validaciones import exigir_existente


class ServicioStock:
    """CRUD del stock más los movimientos de ingreso y retiro de
    unidades."""

    def __init__(self, repositorio: IRepositorioStock,
                 libros: IRepositorio[Libro]) -> None:
        self._repositorio = repositorio
        self._libros = libros

    def crear(self, stock: Stock) -> Stock:
        self._validar(stock)
        if self._repositorio.leer_por_libro(stock.libro_id) is not None:
            raise ValueError("Ese libro ya tiene stock cargado.")
        return self._repositorio.crear(stock)

    def leer_por_libro(self, libro_id: int) -> Optional[Stock]:
        return self._repositorio.leer_por_libro(libro_id)

    def leer_todos(self) -> List[Stock]:
        return self._repositorio.leer_todos()

    def actualizar(self, stock: Stock) -> Stock:
        self._validar(stock)
        self._buscar(stock.libro_id)
        return self._repositorio.actualizar(stock)

    def eliminar(self, libro_id: int) -> bool:
        return self._repositorio.eliminar(libro_id)

    def ingresar(self, libro_id: int, cantidad: int) -> Stock:
        """Suma unidades al stock de un libro (por ejemplo, al recibir un
        pedido de la editorial)."""
        if cantidad <= 0:
            raise ValueError("La cantidad a ingresar debe ser mayor a 0.")
        stock = self._buscar(libro_id)
        stock.cantidad += cantidad
        return self._repositorio.actualizar(stock)

    def retirar(self, libro_id: int, cantidad: int) -> Stock:
        """Resta unidades del stock (por ejemplo, al vender). No deja
        sacar más de lo que hay."""
        if cantidad <= 0:
            raise ValueError("La cantidad a retirar debe ser mayor a 0.")
        stock = self._buscar(libro_id)
        if cantidad > stock.cantidad:
            raise ValueError(
                f"No hay suficiente stock: quedan {stock.cantidad} unidades."
            )
        stock.cantidad -= cantidad
        return self._repositorio.actualizar(stock)

    def _buscar(self, libro_id: int) -> Stock:
        stock = self._repositorio.leer_por_libro(libro_id)
        if stock is None:
            raise ValueError("Ese libro no tiene stock cargado.")
        return stock

    def _validar(self, stock: Stock) -> None:
        if not isinstance(stock, Stock):
            raise TypeError("Se esperaba un objeto Stock.")
        exigir_existente(self._libros, stock.libro_id, "libro")
