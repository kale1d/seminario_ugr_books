"""Item Loader con las reglas de limpieza de cada campo del scraper."""

import re
from decimal import Decimal, InvalidOperation
from typing import Optional

from itemloaders.processors import Identity, Join, MapCompose, TakeFirst
from scrapy.loader import ItemLoader

from .items import LibroWebItem


def limpiar_texto(valor: str) -> Optional[str]:
    """Quita espacios y saltos de línea sobrantes, incluido el espacio
    especial (\\xa0) del HTML.

    Args:
        valor (str): Texto extraído del HTML.

    Returns:
        Optional[str]: Texto en una sola línea, o None si quedó vacío
        (así Scrapy descarta el valor).
    """
    texto = " ".join(str(valor).replace("\xa0", " ").split())
    return texto or None


def limpiar_pago(valor: str) -> Optional[str]:
    """Limpia un medio de pago y le saca el ">" con el que Cúspide
    empieza cada uno.

    Args:
        valor (str): Texto de un medio de pago.

    Returns:
        Optional[str]: Medio de pago sin el prefijo, o None si quedó vacío.
    """
    texto = limpiar_texto(valor)
    if texto is None:
        return None
    return texto.removeprefix(">").strip() or None


def convertir_precio(valor: str) -> Optional[Decimal]:
    """Convierte un precio como "48.500,00" en un Decimal (48500.00).

    En el formato argentino el punto separa miles y la coma, los
    decimales.

    Args:
        valor (str): Texto del precio.

    Returns:
        Optional[Decimal]: El precio, o None si no se pudo interpretar.
    """
    numero = re.sub(r"[^\d,.]", "", valor)
    if not numero:
        return None
    numero = numero.replace(".", "").replace(",", ".")
    try:
        return Decimal(numero)
    except InvalidOperation:
        return None


class LibroWebLoader(ItemLoader):
    """Carga un LibroWebItem aplicando las reglas de limpieza de cada
    campo."""

    default_item_class = LibroWebItem
    # Salvo que se indique otra cosa, de cada campo se toma el primer valor
    default_output_processor = TakeFirst()

    titulo_catalogo_in = MapCompose(limpiar_texto)
    titulo_web_in = MapCompose(limpiar_texto)
    isbn_in = MapCompose(limpiar_texto)
    precio_in = MapCompose(limpiar_texto, convertir_precio)
    precio_usd_in = MapCompose(limpiar_texto, convertir_precio)

    # La descripción puede venir en varios fragmentos: se unen en un texto
    descripcion_in = MapCompose(limpiar_texto)
    descripcion_out = Join(" ")

    # Los medios de pago son varios: se conservan como lista
    formas_pago_in = MapCompose(limpiar_pago)
    formas_pago_out = Identity()