"""Servicio de stock: CRUD y movimientos de unidades."""

from typing import List, Optional

from ..entities.libro import Libro
from ..entities.stock import Stock
from ..repositories.interfaces import IRepositorio, IRepositorioStock
from .servicio_auditoria import ServicioAuditoria, auditar
from .validaciones import exigir_existente


class ServicioStock:
    """CRUD del stock más los movimientos de ingreso y retiro de
    unidades."""

    def __init__(self, repositorio: IRepositorioStock,
                 libros: IRepositorio[Libro],
                 auditoria: Optional[ServicioAuditoria] = None) -> None:
        """Guarda el repositorio de stock, el de libros y el servicio de
        auditoría."""
        self._repositorio = repositorio
        self._libros = libros
        self._auditoria = auditoria

    @auditar("Crear")
    def crear(self, stock: Stock) -> Stock:
        """Valida y guarda el stock de un libro.

        Raises:
            ValueError: Si el libro ya tiene stock cargado.
        """
        self._validar(stock)
        if self._repositorio.leer_por_libro(stock.libro_id) is not None:
            raise ValueError("Ese libro ya tiene stock cargado.")
        return self._repositorio.crear(stock)

    def leer_por_libro(self, libro_id: int) -> Optional[Stock]:
        """Devuelve el stock de un libro, o None si no tiene."""
        return self._repositorio.leer_por_libro(libro_id)

    def leer_todos(self) -> List[Stock]:
        """Devuelve el stock de todos los libros."""
        return self._repositorio.leer_todos()

    @auditar("Actualizar")
    def actualizar(self, stock: Stock) -> Stock:
        """Valida y actualiza el stock de un libro."""
        self._validar(stock)
        self._buscar(stock.libro_id)
        return self._repositorio.actualizar(stock)

    @auditar("Eliminar")
    def eliminar(self, libro_id: int) -> bool:
        """Elimina el stock de un libro."""
        return self._repositorio.eliminar(libro_id)

    @auditar("Ingresar stock")
    def ingresar(self, libro_id: int, cantidad: int) -> Stock:
        """Suma unidades al stock de un libro (por ejemplo, al recibir un
        pedido de la editorial)."""
        if cantidad <= 0:
            raise ValueError("La cantidad a ingresar debe ser mayor a 0.")
        stock = self._buscar(libro_id)
        stock.cantidad += cantidad
        return self._repositorio.actualizar(stock)

    @auditar("Retirar stock")
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
        """Devuelve el stock de un libro o lanza ValueError si no tiene."""
        stock = self._repositorio.leer_por_libro(libro_id)
        if stock is None:
            raise ValueError("Ese libro no tiene stock cargado.")
        return stock

    def _validar(self, stock: Stock) -> None:
        """Verifica el tipo de objeto y que el libro exista."""
        if not isinstance(stock, Stock):
            raise TypeError("Se esperaba un objeto Stock.")
        exigir_existente(self._libros, stock.libro_id, "libro")
