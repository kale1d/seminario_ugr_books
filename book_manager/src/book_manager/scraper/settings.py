"""Configuración de Scrapy para el spider de Cúspide.

Se aplican reglas de cortesía con el sitio: se respeta el robots.txt, se
hace una sola petición a la vez y se deja una pausa entre ellas.
"""

BOT_NAME = "book_manager"
SPIDER_MODULES = ["book_manager.scraper.spiders"]

# El robots.txt de Cúspide solo restringe /cgi-bin/, así que las búsquedas
# y las fichas de producto están permitidas.
ROBOTSTXT_OBEY = True

# Una petición a la vez y 1,5 segundos de pausa entre ellas.
CONCURRENT_REQUESTS = 1
DOWNLOAD_DELAY = 1.5

# Si una página no responde, se espera como máximo 30 segundos y se
# reintenta hasta 2 veces.
DOWNLOAD_TIMEOUT = 30
RETRY_ENABLED = True
RETRY_TIMES = 2

FEED_EXPORT_ENCODING = "utf-8"
LOG_LEVEL = "INFO"

# Etapas por las que pasa cada item, de menor a mayor número.
ITEM_PIPELINES = {
    "book_manager.scraper.pipelines.ValidacionPipeline": 100,
    "book_manager.scraper.pipelines.DuplicadosPipeline": 200,
    "book_manager.scraper.pipelines.PersistenciaPipeline": 300,
}