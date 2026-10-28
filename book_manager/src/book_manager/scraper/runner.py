"""Ejecuta el spider de Cúspide en un proceso independiente.

El reactor de Twisted no se puede reiniciar dentro del mismo proceso, por
eso cada scraping se lanza con "python -m book_manager.scraper.runner" y
arranca con un reactor nuevo.
"""

import sys
from typing import Optional

from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from .spiders.cuspide import CuspideSpider


def ejecutar(libro_id: Optional[str] = None) -> None:
    """Lanza el scraping y espera a que termine.

    Args:
        libro_id (Optional[str]): Si se indica, se busca solo ese libro
            del catálogo; si no, se buscan todos.
    """
    configuracion = Settings()
    configuracion.setmodule("book_manager.scraper.settings",
                            priority="project")
    proceso = CrawlerProcess(configuracion)
    proceso.crawl(CuspideSpider, libro_id=libro_id)
    proceso.start()


if __name__ == "__main__":
    ejecutar(sys.argv[1] if len(sys.argv) > 1 else None)