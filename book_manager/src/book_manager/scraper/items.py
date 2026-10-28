"""Items del scraper: estructura de los datos extraídos de Cúspide."""

import scrapy


class LibroWebItem(scrapy.Item):
    """Datos de un libro extraídos de su ficha en Cúspide.

    Attributes:
        libro_id: ID del libro del catálogo propio que originó la búsqueda.
        titulo_catalogo: Título del catálogo propio con el que se buscó.
        titulo_web: Título publicado en Cúspide.
        isbn: ISBN que figura en la ficha.
        precio: Precio en pesos.
        precio_usd: Precio de referencia en dólares, si el sitio lo publica.
        url_imagen: URL de la imagen de tapa.
        formas_pago: Medios de pago que informa el sitio.
        descripcion: Descripción detallada (sinopsis).
        url_detalle: URL de la ficha del libro.
        fecha_extraccion: Fecha y hora en que se extrajo el dato.
    """

    libro_id = scrapy.Field()
    titulo_catalogo = scrapy.Field()
    titulo_web = scrapy.Field()
    isbn = scrapy.Field()
    precio = scrapy.Field()
    precio_usd = scrapy.Field()
    url_imagen = scrapy.Field()
    formas_pago = scrapy.Field()
    descripcion = scrapy.Field()
    url_detalle = scrapy.Field()
    fecha_extraccion = scrapy.Field()