from ..entities.editorial import Editorial
from ..entities.genero import Genero
from ..entities.libro import Libro
from ..repositories.interfaces import IRepositorio
from .servicio_base import ServicioBase
from .validaciones import exigir_existente


class ServicioLibro(ServicioBase[Libro]):
    """La editorial y el género tienen que existir y el ISBN no se puede
    repetir."""

    tipo = Libro

    def __init__(self, repositorio: IRepositorio[Libro],
                 editoriales: IRepositorio[Editorial],
                 generos: IRepositorio[Genero]) -> None:
        super().__init__(repositorio)
        self._editoriales = editoriales
        self._generos = generos

    def _validar(self, entidad: Libro) -> None:
        super()._validar(entidad)
        exigir_existente(self._editoriales, entidad.editorial.id, "editorial")
        exigir_existente(self._generos, entidad.genero.id, "género")
        isbn = self._limpiar_isbn(entidad.isbn)
        for libro in self._repositorio.leer_todos():
            if libro.id == entidad.id:
                continue
            if self._limpiar_isbn(libro.isbn) == isbn:
                raise ValueError("Ya existe un libro con ese ISBN.")

    @staticmethod
    def _limpiar_isbn(isbn: str) -> str:
        """Saca guiones y espacios para comparar, así "978-84" y "97884"
        se toman como el mismo ISBN."""
        return isbn.replace("-", "").replace(" ", "").upper()
