from typing import Generic, List, Optional, TypeVar

from ..entities.entidad_base import EntidadBase
from ..repositories.interfaces import IRepositorio

T = TypeVar("T", bound=EntidadBase)


class ServicioBase(Generic[T]):
    """CRUD con las reglas de negocio comunes a las entidades con ID.

    Los servicios hijos sobrescriben _validar() para agregar sus propias
    reglas (por ejemplo, que no se repita el ISBN de un libro).
    """

    tipo: type

    def __init__(self, repositorio: IRepositorio[T]) -> None:
        self._repositorio = repositorio

    def crear(self, entidad: T) -> T:
        self._validar(entidad)
        if self._repositorio.leer_por_id(entidad.id) is not None:
            raise ValueError(f"Ya existe un registro con ID {entidad.id}.")
        return self._repositorio.crear(entidad)

    def leer_por_id(self, id: int) -> Optional[T]:
        return self._repositorio.leer_por_id(id)

    def leer_todos(self) -> List[T]:
        return self._repositorio.leer_todos()

    def actualizar(self, entidad: T) -> T:
        self._validar(entidad)
        if self._repositorio.leer_por_id(entidad.id) is None:
            raise ValueError(f"No existe un registro con ID {entidad.id}.")
        return self._repositorio.actualizar(entidad)

    def eliminar(self, id: int) -> bool:
        """Si el registro está siendo usado por otro, el repositorio
        lanza ValueError y no se borra."""
        return self._repositorio.eliminar(id)

    def _validar(self, entidad: T) -> None:
        if not isinstance(entidad, self.tipo):
            raise TypeError(f"Se esperaba un objeto {self.tipo.__name__}.")
