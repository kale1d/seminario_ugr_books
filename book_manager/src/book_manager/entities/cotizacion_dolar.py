from datetime import date
from decimal import Decimal
from typing import Union

from .tipo_cotizacion import TipoCotizacion
from .validaciones import validar_importe, validar_tipo


class CotizacionDolar:
    """Valor de compra y venta del dólar (en pesos) para un tipo y fecha.

    Tipo + fecha funcionan como clave del histórico, por eso no tienen
    setter.
    """

    def __init__(self, tipo: TipoCotizacion, fecha: date,
                 compra: Union[Decimal, int, float, str],
                 venta: Union[Decimal, int, float, str]) -> None:
        validar_tipo(tipo, TipoCotizacion, "El tipo de cotización")
        validar_tipo(fecha, date, "La fecha")
        self.__tipo = tipo
        self.__fecha = fecha
        self.compra = compra
        self.venta = venta

    @property
    def tipo(self) -> TipoCotizacion:
        return self.__tipo

    @property
    def tipo_id(self) -> int:
        """ID del tipo, que es lo que usa el repositorio para buscar."""
        return self.__tipo.id

    @property
    def fecha(self) -> date:
        return self.__fecha

    @property
    def compra(self) -> Decimal:
        return self.__compra

    @compra.setter
    def compra(self, valor: Union[Decimal, int, float, str]) -> None:
        importe = validar_importe(valor)
        if importe == 0:
            raise ValueError("La cotización de compra no puede ser 0.")
        self.__compra = importe

    @property
    def venta(self) -> Decimal:
        return self.__venta

    @venta.setter
    def venta(self, valor: Union[Decimal, int, float, str]) -> None:
        importe = validar_importe(valor)
        if importe == 0:
            raise ValueError("La cotización de venta no puede ser 0.")
        self.__venta = importe

    def __str__(self) -> str:
        return (f"Dólar {self.tipo} {self.fecha:%d/%m/%Y}: "
                f"compra ${self.compra} / venta ${self.venta}")
