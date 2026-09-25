from sqlite3 import Row

from ..entities.moneda import Moneda
from .repositorio_base import RepositorioBase


class RepositorioMoneda(RepositorioBase[Moneda]):
    tabla = "monedas"
    columnas = ("nombre", "codigo")
    tipo = Moneda

    def _a_fila(self, entidad: Moneda) -> tuple:
        return (entidad.nombre, entidad.codigo)

    def _desde_fila(self, fila: Row) -> Moneda:
        return Moneda(fila["id"], fila["nombre"], fila["codigo"])
