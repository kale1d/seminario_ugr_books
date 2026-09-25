from sqlite3 import Row

from ..entities.libro import Libro
from .base_de_datos import BaseDeDatos
from .repositorio_base import RepositorioBase
from .repositorio_editorial import RepositorioEditorial
from .repositorio_genero import RepositorioGenero


class RepositorioLibro(RepositorioBase[Libro]):
    """En la tabla se guardan los IDs de la editorial y el género; al leer
    se buscan para devolver el libro con los objetos completos."""

    tabla = "libros"
    columnas = ("isbn", "titulo", "autor", "editorial_id", "genero_id")
    tipo = Libro

    def __init__(self, base: BaseDeDatos) -> None:
        super().__init__(base)
        self._editoriales = RepositorioEditorial(base)
        self._generos = RepositorioGenero(base)

    def _a_fila(self, entidad: Libro) -> tuple:
        return (entidad.isbn, entidad.titulo, entidad.autor,
                entidad.editorial.id, entidad.genero.id)

    def _desde_fila(self, fila: Row) -> Libro:
        editorial = self._editoriales.leer_por_id(fila["editorial_id"])
        genero = self._generos.leer_por_id(fila["genero_id"])
        if editorial is None or genero is None:
            raise ValueError(f"El libro {fila['id']} tiene datos rotos.")
        return Libro(fila["id"], fila["isbn"], fila["titulo"],
                     fila["autor"], editorial, genero)
