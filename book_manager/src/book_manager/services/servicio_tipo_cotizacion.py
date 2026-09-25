from ..entities.tipo_cotizacion import TipoCotizacion
from .servicio_base import ServicioBase


class ServicioTipoCotizacion(ServicioBase[TipoCotizacion]):
    """No tiene reglas extra: el nombre ya lo valida la entidad."""

    tipo = TipoCotizacion
