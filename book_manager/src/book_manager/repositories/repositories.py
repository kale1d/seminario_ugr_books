"""Repositorios del gestor de libros.

Cada repositorio está en su propio archivo; acá se importan todos juntos
para usarlos desde un solo lugar.
"""

from .base_de_datos import BaseDeDatos
from .interfaces import (IRepositorio, IRepositorioCotizacionDolar,
                         IRepositorioStock)
from .repositorio_base import RepositorioBase
from .repositorio_genero import RepositorioGenero
from .repositorio_editorial import RepositorioEditorial
from .repositorio_moneda import RepositorioMoneda
from .repositorio_tipo_cotizacion import RepositorioTipoCotizacion
from .repositorio_libro import RepositorioLibro
from .repositorio_precio import RepositorioPrecio
from .repositorio_stock import RepositorioStock
from .repositorio_cotizacion_dolar import RepositorioCotizacionDolar
