"""Servicio de cotizaciones del dólar: CRUD, última cotización vigente y
descarga desde la API web."""

import json
import os
import urllib.error
import urllib.request
from datetime import date, datetime
from typing import Dict, List, Optional

from ..entities.cotizacion_dolar import CotizacionDolar
from ..entities.tipo_cotizacion import TipoCotizacion
from ..repositories.interfaces import IRepositorio, IRepositorioCotizacionDolar
from .validaciones import exigir_existente

# Segundos máximos de espera de la API antes de abandonar la consulta.
TIMEOUT_API = 10

# Nombres con los que la API identifica a algunas casas que en la base
# se llaman distinto.
ALIAS_CASAS: Dict[str, str] = {
    "bolsa": "MEP",
    "contadoconliqui": "CCL",
}


class ServicioCotizacionDolar:
    """CRUD del histórico de cotizaciones, búsqueda de la última
    cotización vigente y descarga de cotizaciones desde la API."""

    def __init__(self, repositorio: IRepositorioCotizacionDolar,
                 tipos: IRepositorio[TipoCotizacion]) -> None:
        """Guarda los repositorios que usa el servicio.

        Args:
            repositorio (IRepositorioCotizacionDolar): Repositorio de
                cotizaciones.
            tipos (IRepositorio[TipoCotizacion]): Repositorio de tipos de
                cotización.
        """
        self._repositorio = repositorio
        self._tipos = tipos

    def crear(self, cotizacion: CotizacionDolar) -> CotizacionDolar:
        """Guarda una cotización nueva.

        Raises:
            ValueError: Si ya hay una cotización para ese tipo y fecha.
        """
        self._validar(cotizacion)
        existente = self._repositorio.leer_por_tipo_y_fecha(
            cotizacion.tipo_id, cotizacion.fecha
        )
        if existente is not None:
            raise ValueError("Ya hay una cotización para ese tipo y fecha.")
        return self._repositorio.crear(cotizacion)

    def leer_por_tipo_y_fecha(self, tipo_id: int,
                              fecha: date) -> Optional[CotizacionDolar]:
        """Devuelve la cotización de un tipo en una fecha, o None."""
        return self._repositorio.leer_por_tipo_y_fecha(tipo_id, fecha)

    def leer_historico_por_tipo(self, tipo_id: int) -> List[CotizacionDolar]:
        """Devuelve el histórico de un tipo, de la más vieja a la más
        nueva."""
        return self._repositorio.leer_historico_por_tipo(tipo_id)

    def leer_todos(self) -> List[CotizacionDolar]:
        """Devuelve todas las cotizaciones guardadas."""
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
        """Actualiza una cotización existente.

        Raises:
            ValueError: Si no hay cotización para ese tipo y fecha.
        """
        self._validar(cotizacion)
        existente = self._repositorio.leer_por_tipo_y_fecha(
            cotizacion.tipo_id, cotizacion.fecha
        )
        if existente is None:
            raise ValueError("No hay cotización para ese tipo y fecha.")
        return self._repositorio.actualizar(cotizacion)

    def eliminar(self, tipo_id: int, fecha: date) -> bool:
        """Elimina la cotización de un tipo en una fecha."""
        return self._repositorio.eliminar(tipo_id, fecha)

    def obtener_cotizaciones(self) -> List[CotizacionDolar]:
        """Descarga las cotizaciones de la API y las registra en la base.

        La URL se toma de la variable de entorno API_URL. Cada cotización
        se guarda con la fecha de ``fechaActualizacion`` que informa la
        API; si ya existía una para ese tipo y fecha, se actualiza. Los
        tipos que todavía no están cargados se dan de alta.

        Returns:
            List[CotizacionDolar]: Las cotizaciones guardadas.

        Raises:
            ValueError: Si falta API_URL, si la API no responde o si la
                respuesta no tiene el formato esperado.
        """
        url_api = os.getenv("API_URL")
        if not url_api:
            raise ValueError("No se encontró API_URL en el archivo .env")

        guardadas = []
        for dato in self._descargar(url_api):
            casa = dato.get("casa")
            compra = dato.get("compra")
            venta = dato.get("venta")
            if not casa or not compra or not venta:
                continue
            tipo = self._buscar_o_crear_tipo(casa)
            fecha = self._fecha_de(dato)
            nueva = CotizacionDolar(tipo, fecha, compra, venta)
            if self._repositorio.leer_por_tipo_y_fecha(tipo.id, fecha):
                self._repositorio.actualizar(nueva)
            else:
                self._repositorio.crear(nueva)
            guardadas.append(nueva)
        return guardadas

    @staticmethod
    def _descargar(url_api: str) -> List[dict]:
        """Consulta la API y devuelve la lista de cotizaciones (JSON).

        Raises:
            ValueError: Si hay un error de conexión, se agota el tiempo de
                espera o la respuesta no es una lista JSON.
        """
        peticion = urllib.request.Request(
            url_api, headers={"User-Agent": "Mozilla/5.0"}
        )
        try:
            with urllib.request.urlopen(peticion,
                                        timeout=TIMEOUT_API) as respuesta:
                datos = json.loads(respuesta.read().decode("utf-8"))
        except (urllib.error.URLError, TimeoutError) as error:
            raise ValueError(f"No se pudo consultar la API: {error}") \
                from error
        except json.JSONDecodeError as error:
            raise ValueError("La API devolvió una respuesta inválida.") \
                from error
        if not isinstance(datos, list):
            raise ValueError("La API devolvió un formato inesperado.")
        return datos

    @staticmethod
    def _fecha_de(dato: dict) -> date:
        """Toma la fecha de ``fechaActualizacion`` (ISO 8601). Si la API
        no la informa o no se puede leer, usa la fecha de hoy."""
        texto = dato.get("fechaActualizacion")
        if texto:
            try:
                return datetime.fromisoformat(
                    texto.replace("Z", "+00:00")
                ).date()
            except ValueError:
                pass
        return date.today()

    def _buscar_o_crear_tipo(self, casa: str) -> TipoCotizacion:
        """Busca el tipo de cotización de una casa de la API; si no está
        cargado, lo da de alta con el siguiente ID libre."""
        nombre = ALIAS_CASAS.get(casa.lower(), casa)
        tipos = self._tipos.leer_todos()
        for tipo in tipos:
            if tipo.nombre.lower() == nombre.lower():
                return tipo
        # Se guarda con el nombre de la casa para encontrarlo la próxima vez
        nuevo = TipoCotizacion(
            max((t.id for t in tipos), default=0) + 1, nombre.capitalize()
        )
        return self._tipos.crear(nuevo)

    def _validar(self, cotizacion: CotizacionDolar) -> None:
        """Verifica el tipo de objeto y que exista su tipo de cotización.

        Raises:
            TypeError: Si no es una CotizacionDolar.
            ValueError: Si el tipo de cotización no existe.
        """
        if not isinstance(cotizacion, CotizacionDolar):
            raise TypeError("Se esperaba un objeto CotizacionDolar.")
        exigir_existente(self._tipos, cotizacion.tipo_id,
                         "tipo de cotización")
