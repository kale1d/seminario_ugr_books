from sqlite3 import Row

from ..entities.editorial import Editorial
from .repositorio_base import RepositorioBase


class RepositorioEditorial(RepositorioBase[Editorial]):
    tabla = "editoriales"
    columnas = ("nombre",)
    tipo = Editorial

    def _a_fila(self, entidad: Editorial) -> tuple:
        return (entidad.nombre,)

    def _desde_fila(self, fila: Row) -> Editorial:
        return Editorial(fila["id"], fila["nombre"])
