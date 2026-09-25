"""Entidades del gestor de libros.

Cada clase está en su propio archivo para que sea más fácil de leer,
y acá se importan todas juntas para usarlas desde un solo lugar.
"""

from .entidad_base import EntidadBase, EntidadConNombre
from .genero import Genero
from .editorial import Editorial
from .tipo_cotizacion import TipoCotizacion
from .moneda import Moneda
from .libro import Libro
from .precio import Precio
from .stock import Stock
from .cotizacion_dolar import CotizacionDolar
