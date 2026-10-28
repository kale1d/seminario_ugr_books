"""Spider de Cúspide: busca los libros del catálogo y extrae sus fichas."""

from datetime import datetime
from typing import AsyncIterator, Optional
from urllib.parse import quote_plus

import scrapy
from scrapy.http import Response

from ...database.connection import ConexionDB
from ...entities.libro import Libro
from ...repositories.repositories import RepositorioLibro
from ..loader import LibroWebLoader


class CuspideSpider(scrapy.Spider):
    """Busca cada título del catálogo en Cúspide y extrae las fichas de
    los 10 primeros resultados.

    Solo se buscan libros del catálogo propio, que se leen de la base de
    datos.

    Args:
        libro_id (Optional[str]): Si se indica, se busca solo ese libro
            del catálogo (útil para probar sin recorrer todo).
    """

    name = "cuspide"
    allowed_domains = ["cuspide.com"]
    url_busqueda = "https://cuspide.com/?s={consulta}&post_type=product"
    max_resultados = 10

    def __init__(self, libro_id: Optional[str] = None, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.libros = self._leer_libros(libro_id)
        self.fecha_extraccion = datetime.now()

    @staticmethod
    def _leer_libros(libro_id: Optional[str]) -> list[Libro]:
        """Lee los libros del catálogo (o solo el indicado)."""
        libros = RepositorioLibro(ConexionDB()).leer_todos()
        if libro_id is not None:
            libros = [libro for libro in libros if libro.id == int(libro_id)]
        return libros

    async def start(self) -> AsyncIterator[scrapy.Request]:
        """Genera una búsqueda por cada libro del catálogo."""
        for libro in self.libros:
            url = self.url_busqueda.format(consulta=quote_plus(libro.titulo))
            yield scrapy.Request(url, callback=self.parse_busqueda,
                                 cb_kwargs={"libro": libro})

    def parse_busqueda(self, response: Response, libro: Libro):
        """Toma las fichas de los primeros resultados de la búsqueda."""
        enlaces = response.css(
            "div.product p.woocommerce-loop-product__title a::attr(href)"
        ).getall()
        for url in enlaces[:self.max_resultados]:
            # dont_filter: dos libros del catálogo pueden dar la misma
            # ficha y cada uno tiene que quedar registrado.
            yield response.follow(url, callback=self.parse_ficha,
                                  cb_kwargs={"libro": libro},
                                  dont_filter=True)

    def parse_ficha(self, response: Response, libro: Libro):
        """Extrae los datos de la ficha de un libro."""
        cargador = LibroWebLoader(response=response)
        cargador.add_value("libro_id", libro.id)
        cargador.add_value("titulo_catalogo", libro.titulo)
        cargador.add_css("titulo_web", "h1::text")
        cargador.add_css("isbn", "span.sku::text")
        cargador.add_css("precio", "p.price bdi::text")
        cargador.add_xpath("precio_usd",
                           '//span[contains(text(),"U$s")]/span/text()')
        cargador.add_css("url_imagen", "div.woocommerce-product-gallery "
                         "img::attr(data-large_image)")
        cargador.add_css("formas_pago", "#contentPaymentsPopUpArg li::text")
        cargador.add_css("descripcion", "p.livriz-text-synopsis ::text")
        cargador.add_value("url_detalle", response.url)
        cargador.add_value("fecha_extraccion", self.fecha_extraccion)
        yield cargador.load_item()