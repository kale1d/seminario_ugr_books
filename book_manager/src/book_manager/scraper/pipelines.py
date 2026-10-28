"""Pipelines del scraper: validación, duplicados y guardado en la base."""

from typing import Any

from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem

from ..database.connection import ConexionDB
from ..models.models import PrecioWebModel


class ValidacionPipeline:
    """Descarta los items que no tienen los datos mínimos para comparar."""

    def process_item(self, item: Any) -> Any:
        """Verifica que el item tenga libro del catálogo y precio web.

        Raises:
            DropItem: Si falta el libro de origen o el precio.
        """
        datos = ItemAdapter(item)
        if datos.get("libro_id") is None:
            raise DropItem("Item sin libro del catálogo de origen.")
        if datos.get("precio") is None:
            raise DropItem(f"Sin precio web para {datos.get('titulo_web')!r}")
        return item


class DuplicadosPipeline:
    """Evita guardar dos veces la misma ficha para el mismo libro dentro
    de una ejecución."""

    def open_spider(self) -> None:
        """Prepara el registro de fichas ya vistas."""
        self.vistos: set[tuple] = set()

    def process_item(self, item: Any) -> Any:
        """Descarta el item si esa ficha ya se procesó para ese libro.

        Raises:
            DropItem: Si el par (libro, ficha) ya fue procesado.
        """
        datos = ItemAdapter(item)
        clave = (datos.get("libro_id"), datos.get("url_detalle"))
        if clave in self.vistos:
            raise DropItem(f"Ficha repetida: {clave[1]}")
        self.vistos.add(clave)
        return item


class PersistenciaPipeline:
    """Guarda cada item en la tabla precios_web de la base de datos."""

    def open_spider(self) -> None:
        """Abre la conexión y se asegura de que existan las tablas."""
        self.db = ConexionDB()
        self.db.crear_tablas()

    def process_item(self, item: Any) -> Any:
        """Inserta una fila en precios_web con los datos del item."""
        datos = ItemAdapter(item)
        with self.db.obtener_sesion() as sesion:
            sesion.add(PrecioWebModel(
                libro_id=datos.get("libro_id"),
                titulo_web=datos.get("titulo_web"),
                isbn=datos.get("isbn"),
                precio=datos.get("precio"),
                precio_usd=datos.get("precio_usd"),
                url_imagen=datos.get("url_imagen"),
                formas_pago=datos.get("formas_pago"),
                descripcion=datos.get("descripcion"),
                url_detalle=datos.get("url_detalle"),
                fecha_extraccion=datos.get("fecha_extraccion"),
            ))
        return item