from abc import abstractmethod
from sqlite3 import Row
from typing import List, Optional

from .base_de_datos import BaseDeDatos
from .interfaces import IRepositorio, T


class RepositorioBase(IRepositorio[T]):
    """CRUD genérico para las entidades que se buscan por ID.

    Cada repositorio hijo solo tiene que indicar su tabla, sus columnas
    y cómo pasar la entidad a una fila y viceversa. Los nombres de tabla
    y columnas son fijos en el código, nunca vienen del usuario.
    """

    tabla: str
    columnas: tuple
    tipo: type

    def __init__(self, base: BaseDeDatos) -> None:
        self._base = base

    def crear(self, entidad: T) -> T:
        self._validar_tipo(entidad)
        columnas = ", ".join(("id",) + self.columnas)
        signos = ", ".join(["?"] * (len(self.columnas) + 1))
        self._base.ejecutar(
            f"INSERT INTO {self.tabla} ({columnas}) VALUES ({signos})",
            (entidad.id,) + self._a_fila(entidad),
        )
        return entidad

    def leer_por_id(self, id: int) -> Optional[T]:
        filas = self._base.consultar(
            f"SELECT * FROM {self.tabla} WHERE id = ?", (id,)
        )
        if not filas:
            return None
        return self._desde_fila(filas[0])

    def leer_todos(self) -> List[T]:
        filas = self._base.consultar(f"SELECT * FROM {self.tabla} ORDER BY id")
        return [self._desde_fila(fila) for fila in filas]

    def actualizar(self, entidad: T) -> T:
        self._validar_tipo(entidad)
        campos = ", ".join(f"{columna} = ?" for columna in self.columnas)
        modificadas = self._base.ejecutar(
            f"UPDATE {self.tabla} SET {campos} WHERE id = ?",
            self._a_fila(entidad) + (entidad.id,),
        )
        if modificadas == 0:
            raise ValueError(f"No existe el registro con ID {entidad.id}.")
        return entidad

    def eliminar(self, id: int) -> bool:
        borradas = self._base.ejecutar(
            f"DELETE FROM {self.tabla} WHERE id = ?", (id,)
        )
        return borradas > 0

    def _validar_tipo(self, entidad: T) -> None:
        if not isinstance(entidad, self.tipo):
            raise TypeError(f"Se esperaba un objeto {self.tipo.__name__}.")

    @abstractmethod
    def _a_fila(self, entidad: T) -> tuple:
        """Devuelve los valores de las columnas (sin el ID)."""

    @abstractmethod
    def _desde_fila(self, fila: Row) -> T:
        """Arma la entidad a partir de una fila de la tabla."""
