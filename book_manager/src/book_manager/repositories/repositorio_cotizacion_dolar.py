import datetime
from sqlite3 import Row
from typing import List, Optional

from ..entities.cotizacion_dolar import CotizacionDolar
from .base_de_datos import BaseDeDatos
from .interfaces import IRepositorioCotizacionDolar
from .repositorio_tipo_cotizacion import RepositorioTipoCotizacion


class RepositorioCotizacionDolar(IRepositorioCotizacionDolar):
    """Histórico de cotizaciones: una por cada tipo y fecha.

    La fecha se guarda como texto AAAA-MM-DD y los importes como texto
    para no perder precisión del Decimal.
    """

    def __init__(self, base: BaseDeDatos) -> None:
        self._base = base
        self._tipos = RepositorioTipoCotizacion(base)

    def crear(self, cotizacion: CotizacionDolar) -> CotizacionDolar:
        self._validar_tipo(cotizacion)
        self._base.ejecutar(
            "INSERT INTO cotizaciones_dolar (tipo_id, fecha, compra, venta) "
            "VALUES (?, ?, ?, ?)",
            (cotizacion.tipo_id, self._fecha_a_texto(cotizacion.fecha),
             str(cotizacion.compra), str(cotizacion.venta)),
        )
        return cotizacion

    def leer_por_tipo_y_fecha(
        self, tipo_id: int, fecha: datetime.date
    ) -> Optional[CotizacionDolar]:
        filas = self._base.consultar(
            "SELECT * FROM cotizaciones_dolar WHERE tipo_id = ? AND fecha = ?",
            (tipo_id, self._fecha_a_texto(fecha)),
        )
        if not filas:
            return None
        return self._desde_fila(filas[0])

    def leer_historico_por_tipo(self, tipo_id: int) -> List[CotizacionDolar]:
        """Devuelve las cotizaciones del tipo, de la más vieja a la más
        nueva."""
        filas = self._base.consultar(
            "SELECT * FROM cotizaciones_dolar WHERE tipo_id = ? "
            "ORDER BY fecha",
            (tipo_id,),
        )
        return [self._desde_fila(fila) for fila in filas]

    def leer_todos(self) -> List[CotizacionDolar]:
        filas = self._base.consultar(
            "SELECT * FROM cotizaciones_dolar ORDER BY tipo_id, fecha"
        )
        return [self._desde_fila(fila) for fila in filas]

    def actualizar(self, cotizacion: CotizacionDolar) -> CotizacionDolar:
        self._validar_tipo(cotizacion)
        modificadas = self._base.ejecutar(
            "UPDATE cotizaciones_dolar SET compra = ?, venta = ? "
            "WHERE tipo_id = ? AND fecha = ?",
            (str(cotizacion.compra), str(cotizacion.venta),
             cotizacion.tipo_id, self._fecha_a_texto(cotizacion.fecha)),
        )
        if modificadas == 0:
            raise ValueError("No hay cotización cargada para ese tipo y "
                             "fecha.")
        return cotizacion

    def eliminar(self, tipo_id: int, fecha: datetime.date) -> bool:
        borradas = self._base.ejecutar(
            "DELETE FROM cotizaciones_dolar WHERE tipo_id = ? AND fecha = ?",
            (tipo_id, self._fecha_a_texto(fecha)),
        )
        return borradas > 0

    def _validar_tipo(self, cotizacion: CotizacionDolar) -> None:
        if not isinstance(cotizacion, CotizacionDolar):
            raise TypeError("Se esperaba un objeto CotizacionDolar.")

    def _fecha_a_texto(self, fecha: datetime.date) -> str:
        # strftime y no isoformat: si llega un datetime, isoformat le
        # agrega la hora y ya no coincidiría con lo guardado
        return fecha.strftime("%Y-%m-%d")

    def _desde_fila(self, fila: Row) -> CotizacionDolar:
        tipo = self._tipos.leer_por_id(fila["tipo_id"])
        if tipo is None:
            raise ValueError(f"La cotización del {fila['fecha']} apunta a "
                             "un tipo que no existe.")
        fecha = datetime.date.fromisoformat(fila["fecha"])
        return CotizacionDolar(tipo, fecha, fila["compra"], fila["venta"])
