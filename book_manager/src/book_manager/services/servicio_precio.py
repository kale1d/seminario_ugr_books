from datetime import date
from decimal import Decimal
from typing import Optional

from ..entities.libro import Libro
from ..entities.moneda import Moneda
from ..entities.precio import Precio
from ..repositories.interfaces import IRepositorio
from .servicio_base import ServicioBase
from .servicio_cotizacion_dolar import ServicioCotizacionDolar
from .validaciones import exigir_existente


class ServicioPrecio(ServicioBase[Precio]):
    """Un libro puede tener un solo precio por moneda. También permite
    pasar un precio en dólares a pesos."""

    tipo = Precio

    def __init__(self, repositorio: IRepositorio[Precio],
                 libros: IRepositorio[Libro],
                 monedas: IRepositorio[Moneda],
                 cotizaciones: ServicioCotizacionDolar) -> None:
        super().__init__(repositorio)
        self._libros = libros
        self._monedas = monedas
        self._cotizaciones = cotizaciones

    def _validar(self, entidad: Precio) -> None:
        super()._validar(entidad)
        exigir_existente(self._libros, entidad.libro.id, "libro")
        exigir_existente(self._monedas, entidad.moneda.id, "moneda")
        for precio in self._repositorio.leer_todos():
            if (precio.id != entidad.id
                    and precio.libro.id == entidad.libro.id
                    and precio.moneda.id == entidad.moneda.id):
                raise ValueError("El libro ya tiene precio en esa moneda.")

    def cotizar_en_pesos(self, id: int, tipo_id: int,
                         fecha: Optional[date] = None) -> Decimal:
        """Devuelve el precio en pesos usando el valor de venta del dólar.

        Si el precio ya está en ARS se devuelve tal cual. Si no se pasa
        fecha se usa la última cotización hasta hoy. No modifica el precio
        guardado.
        """
        precio = exigir_existente(self._repositorio, id, "precio")
        if precio.moneda.codigo == "ARS":
            return precio.valor
        if precio.moneda.codigo != "USD":
            raise ValueError("Solo se pueden convertir precios en USD.")
        cotizacion = self._cotizaciones.leer_ultima(tipo_id, fecha)
        if cotizacion is None:
            raise ValueError("No hay cotización cargada para esa fecha.")
        return precio.valor * cotizacion.venta
