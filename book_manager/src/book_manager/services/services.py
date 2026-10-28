"""Servicios del gestor de libros (la lógica de negocio).

Cada servicio está en su propio archivo; acá se importan todos juntos
para usarlos desde un solo lugar.
"""

from .servicio_auditoria import ServicioAuditoria, auditar
from .servicio_base import ServicioBase
from .servicio_genero import ServicioGenero
from .servicio_editorial import ServicioEditorial
from .servicio_moneda import ServicioMoneda
from .servicio_tipo_cotizacion import ServicioTipoCotizacion
from .servicio_libro import ServicioLibro
from .servicio_precio import ServicioPrecio
from .servicio_stock import ServicioStock
from .servicio_cotizacion_dolar import ServicioCotizacionDolar
from .servicio_comparacion import ServicioComparacion
from .servicio_scraping import ServicioScraping
from .servicio_reporte import ServicioReporte
