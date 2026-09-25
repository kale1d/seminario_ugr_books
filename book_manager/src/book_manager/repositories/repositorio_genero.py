from sqlite3 import Row

from ..entities.genero import Genero
from .repositorio_base import RepositorioBase


class RepositorioGenero(RepositorioBase[Genero]):
    tabla = "generos"
    columnas = ("nombre",)
    tipo = Genero

    def _a_fila(self, entidad: Genero) -> tuple:
        return (entidad.nombre,)

    def _desde_fila(self, fila: Row) -> Genero:
        return Genero(fila["id"], fila["nombre"])
