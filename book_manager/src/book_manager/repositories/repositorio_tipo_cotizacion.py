from sqlite3 import Row

from ..entities.tipo_cotizacion import TipoCotizacion
from .repositorio_base import RepositorioBase


class RepositorioTipoCotizacion(RepositorioBase[TipoCotizacion]):
    tabla = "tipos_cotizacion"
    columnas = ("nombre",)
    tipo = TipoCotizacion

    def _a_fila(self, entidad: TipoCotizacion) -> tuple:
        return (entidad.nombre,)

    def _desde_fila(self, fila: Row) -> TipoCotizacion:
        return TipoCotizacion(fila["id"], fila["nombre"])
