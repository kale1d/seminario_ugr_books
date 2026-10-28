"""Precio de un libro obtenido de la web de la competencia."""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import List, Optional


@dataclass(frozen=True)
class PrecioWeb:
    """Datos de un libro extraídos de su ficha en la web.

    Es de solo lectura: representa lo que informó el sitio en una
    extracción determinada.

    Attributes:
        libro_id: ID del libro del catálogo propio que originó la búsqueda.
        titulo_web: Título publicado en el sitio.
        precio: Precio en pesos.
        url_detalle: URL de la ficha del libro.
        fecha_extraccion: Fecha y hora de la extracción.
        isbn: ISBN de la ficha.
        precio_usd: Precio de referencia en dólares, si se publica.
        url_imagen: URL de la imagen de tapa.
        formas_pago: Medios de pago que informa el sitio.
        descripcion: Descripción detallada.
    """

    libro_id: int
    titulo_web: str
    precio: Decimal
    url_detalle: str
    fecha_extraccion: datetime
    isbn: Optional[str] = None
    precio_usd: Optional[Decimal] = None
    url_imagen: Optional[str] = None
    formas_pago: Optional[List[str]] = None
    descripcion: Optional[str] = None