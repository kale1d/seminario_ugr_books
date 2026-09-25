from datetime import date
from typing import List, Optional

from ..entities.cotizacion_dolar import CotizacionDolar
from ..entities.tipo_cotizacion import TipoCotizacion
from ..repositories.interfaces import IRepositorio, IRepositorioCotizacionDolar
from .validaciones import exigir_existente


class ServicioCotizacionDolar:
    """CRUD del histórico de cotizaciones y búsqueda de la última
    cotización vigente."""

    def __init__(self, repositorio: IRepositorioCotizacionDolar,
                 tipos: IRepositorio[TipoCotizacion]) -> None:
        self._repositorio = repositorio
        self._tipos = tipos

    def crear(self, cotizacion: CotizacionDolar) -> CotizacionDolar:
        self._validar(cotizacion)
        existente = self._repositorio.leer_por_tipo_y_fecha(
            cotizacion.tipo_id, cotizacion.fecha
        )
        if existente is not None:
            raise ValueError("Ya hay una cotización para ese tipo y fecha.")
        return self._repositorio.crear(cotizacion)

    def leer_por_tipo_y_fecha(self, tipo_id: int,
                              fecha: date) -> Optional[CotizacionDolar]:
        return self._repositorio.leer_por_tipo_y_fecha(tipo_id, fecha)

    def leer_historico_por_tipo(self, tipo_id: int) -> List[CotizacionDolar]:
        return self._repositorio.leer_historico_por_tipo(tipo_id)

    def leer_todos(self) -> List[CotizacionDolar]:
        return self._repositorio.leer_todos()

    def leer_ultima(self, tipo_id: int,
                    fecha: Optional[date] = None) -> Optional[CotizacionDolar]:
        """Devuelve la cotización más reciente hasta la fecha indicada
        (hoy si no se indica). Devuelve None si no hay ninguna."""
        if fecha is None:
            fecha = date.today()
        ultima = None
        # El histórico viene ordenado de la más vieja a la más nueva
        for cotizacion in self.leer_historico_por_tipo(tipo_id):
            if cotizacion.fecha > fecha:
                break
            ultima = cotizacion
        return ultima

    def actualizar(self, cotizacion: CotizacionDolar) -> CotizacionDolar:
        self._validar(cotizacion)
        existente = self._repositorio.leer_por_tipo_y_fecha(
            cotizacion.tipo_id, cotizacion.fecha
        )
        if existente is None:
            raise ValueError("No hay cotización para ese tipo y fecha.")
        return self._repositorio.actualizar(cotizacion)

    def eliminar(self, tipo_id: int, fecha: date) -> bool:
        return self._repositorio.eliminar(tipo_id, fecha)

    def _validar(self, cotizacion: CotizacionDolar) -> None:
        if not isinstance(cotizacion, CotizacionDolar):
            raise TypeError("Se esperaba un objeto CotizacionDolar.")
        exigir_existente(self._tipos, cotizacion.tipo_id,
                         "tipo de cotización")
