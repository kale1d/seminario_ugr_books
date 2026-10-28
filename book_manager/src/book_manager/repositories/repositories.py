"""Repositorios que guardan y leen las entidades usando SQLAlchemy.

Cada repositorio traduce entre las entidades del dominio (clases puras de
Python) y los modelos de la base de datos.
"""

import datetime
from typing import Generic, List, Optional, TypeVar

from sqlalchemy import and_, func, inspect

from ..database.connection import ConexionDB
from ..entities.cotizacion_dolar import CotizacionDolar
from ..entities.editorial import Editorial
from ..entities.genero import Genero
from ..entities.libro import Libro
from ..entities.moneda import Moneda
from ..entities.precio import Precio
from ..entities.precio_web import PrecioWeb
from ..entities.stock import Stock
from ..entities.tipo_cotizacion import TipoCotizacion
from ..models.models import (
    CotizacionDolarModel, EditorialModel, GeneroModel, LibroModel,
    MonedaModel, PrecioModel, StockModel, TipoCotizacionModel,
    PrecioWebModel
)
from .interfaces import (
    IRepositorio, IRepositorioCotizacionDolar, IRepositorioStock,
    IRepositorioPrecioWeb
)

T = TypeVar("T")


class RepositorioBase(IRepositorio[T], Generic[T]):
    """Repositorio genérico con el CRUD sobre SQLAlchemy.

    Convierte entre entidades y modelos. Las clases hijas indican cómo
    hacerlo implementando ``_a_modelo`` y ``_a_entidad``.
    """

    def __init__(self, db: ConexionDB, modelo_cls: type) -> None:
        """Guarda la conexión y la clase del modelo con el que trabaja.

        Args:
            db (ConexionDB): Conexión a la base de datos.
            modelo_cls (type): Clase del modelo SQLAlchemy de la tabla.
        """
        self.db = db
        self.modelo_cls = modelo_cls

    def _a_modelo(self, entidad: T):
        """Convierte una entidad en un modelo SQL (lo implementan las
        clases hijas)."""
        raise NotImplementedError

    def _a_entidad(self, modelo) -> T:
        """Convierte un modelo SQL en una entidad (lo implementan las
        clases hijas)."""
        raise NotImplementedError

    def crear(self, entidad: T) -> T:
        """Guarda una entidad nueva y la devuelve.

        Args:
            entidad (T): La entidad a crear.

        Returns:
            T: La misma entidad recibida.
        """
        with self.db.obtener_sesion() as sesion:
            modelo = self._a_modelo(entidad)
            sesion.add(modelo)
            sesion.flush()
            # Se devuelve la entidad original para no depender de las
            # relaciones del modelo, que todavía no están cargadas.
            return entidad

    def leer_por_id(self, id: int) -> Optional[T]:
        """Busca una entidad por ID.

        Args:
            id (int): ID de la entidad.

        Returns:
            Optional[T]: La entidad, o None si no existe.
        """
        with self.db.obtener_sesion() as sesion:
            modelo = sesion.get(self.modelo_cls, id)
            return self._a_entidad(modelo) if modelo else None

    def leer_todos(self) -> List[T]:
        """Devuelve todas las entidades de la tabla."""
        with self.db.obtener_sesion() as sesion:
            modelos = sesion.query(self.modelo_cls).all()
            return [self._a_entidad(m) for m in modelos]

    def actualizar(self, entidad: T) -> T:
        """Actualiza una entidad que ya existe.

        Args:
            entidad (T): La entidad con los datos nuevos.

        Returns:
            T: La misma entidad recibida.

        Raises:
            ValueError: Si no existe un registro con esa clave.
        """
        with self.db.obtener_sesion() as sesion:
            modelo = self._a_modelo(entidad)
            clave = inspect(self.modelo_cls).primary_key_from_instance(
                modelo
            )
            if sesion.get(self.modelo_cls, tuple(clave)) is None:
                raise ValueError(
                    f"No existe un registro con clave {tuple(clave)} "
                    "para actualizar."
                )
            sesion.merge(modelo)
            return entidad

    def eliminar(self, id: int) -> bool:
        """Elimina una entidad por ID.

        Args:
            id (int): ID de la entidad.

        Returns:
            bool: True si se eliminó, False si no existía.
        """
        with self.db.obtener_sesion() as sesion:
            modelo = sesion.get(self.modelo_cls, id)
            if modelo:
                sesion.delete(modelo)
                return True
            return False


# --- Repositorios específicos con sus traductores ---


class RepositorioGenero(RepositorioBase[Genero]):
    """Repositorio de géneros."""

    def __init__(self, db: ConexionDB) -> None:
        """Indica el modelo SQL con el que trabaja el repositorio."""
        super().__init__(db, GeneroModel)

    def _a_modelo(self, e: Genero) -> GeneroModel:
        """Convierte la entidad en su modelo SQL."""
        return GeneroModel(id=e.id, nombre=e.nombre)

    def _a_entidad(self, m: GeneroModel) -> Genero:
        """Convierte el modelo SQL en su entidad."""
        return Genero(m.id, m.nombre)


class RepositorioEditorial(RepositorioBase[Editorial]):
    """Repositorio de editoriales."""

    def __init__(self, db: ConexionDB) -> None:
        """Indica el modelo SQL con el que trabaja el repositorio."""
        super().__init__(db, EditorialModel)

    def _a_modelo(self, e: Editorial) -> EditorialModel:
        """Convierte la entidad en su modelo SQL."""
        return EditorialModel(id=e.id, nombre=e.nombre)

    def _a_entidad(self, m: EditorialModel) -> Editorial:
        """Convierte el modelo SQL en su entidad."""
        return Editorial(m.id, m.nombre)


class RepositorioTipoCotizacion(RepositorioBase[TipoCotizacion]):
    """Repositorio de tipos de cotización."""

    def __init__(self, db: ConexionDB) -> None:
        """Indica el modelo SQL con el que trabaja el repositorio."""
        super().__init__(db, TipoCotizacionModel)

    def _a_modelo(self, e: TipoCotizacion) -> TipoCotizacionModel:
        """Convierte la entidad en su modelo SQL."""
        return TipoCotizacionModel(id=e.id, nombre=e.nombre)

    def _a_entidad(self, m: TipoCotizacionModel) -> TipoCotizacion:
        """Convierte el modelo SQL en su entidad."""
        return TipoCotizacion(m.id, m.nombre)


class RepositorioMoneda(RepositorioBase[Moneda]):
    """Repositorio de monedas."""

    def __init__(self, db: ConexionDB) -> None:
        """Indica el modelo SQL con el que trabaja el repositorio."""
        super().__init__(db, MonedaModel)

    def _a_modelo(self, e: Moneda) -> MonedaModel:
        """Convierte la entidad en su modelo SQL."""
        return MonedaModel(id=e.id, nombre=e.nombre, codigo=e.codigo)

    def _a_entidad(self, m: MonedaModel) -> Moneda:
        """Convierte el modelo SQL en su entidad."""
        return Moneda(m.id, m.nombre, m.codigo)


def _libro_a_entidad(m: LibroModel) -> Libro:
    """Arma la entidad Libro (con su editorial y género) desde el modelo."""
    editorial = Editorial(m.editorial.id, m.editorial.nombre)
    genero = Genero(m.genero.id, m.genero.nombre)
    return Libro(m.id, m.isbn, m.titulo, m.autor, editorial, genero)


class RepositorioLibro(RepositorioBase[Libro]):
    """Repositorio de libros."""

    def __init__(self, db: ConexionDB) -> None:
        """Indica el modelo SQL con el que trabaja el repositorio."""
        super().__init__(db, LibroModel)

    def _a_modelo(self, e: Libro) -> LibroModel:
        """Convierte la entidad en su modelo SQL."""
        return LibroModel(id=e.id, isbn=e.isbn, titulo=e.titulo,
                          autor=e.autor, editorial_id=e.editorial.id,
                          genero_id=e.genero.id)

    def _a_entidad(self, m: LibroModel) -> Libro:
        """Convierte el modelo SQL en su entidad."""
        return _libro_a_entidad(m)


class RepositorioPrecio(RepositorioBase[Precio]):
    """Repositorio de precios."""

    def __init__(self, db: ConexionDB) -> None:
        """Indica el modelo SQL con el que trabaja el repositorio."""
        super().__init__(db, PrecioModel)

    def _a_modelo(self, e: Precio) -> PrecioModel:
        """Convierte la entidad en su modelo SQL."""
        return PrecioModel(id=e.id, valor=e.valor, libro_id=e.libro.id,
                           moneda_id=e.moneda.id)

    def _a_entidad(self, m: PrecioModel) -> Precio:
        """Convierte el modelo SQL en su entidad."""
        libro = _libro_a_entidad(m.libro)
        moneda = Moneda(m.moneda.id, m.moneda.nombre, m.moneda.codigo)
        return Precio(m.id, libro, moneda, m.valor)


class RepositorioStock(RepositorioBase[Stock], IRepositorioStock):
    """Repositorio de stock (la clave es el ID del libro)."""

    def __init__(self, db: ConexionDB) -> None:
        """Indica el modelo SQL con el que trabaja el repositorio."""
        super().__init__(db, StockModel)

    def _a_modelo(self, e: Stock) -> StockModel:
        """Convierte la entidad en su modelo SQL."""
        return StockModel(libro_id=e.libro.id, cantidad=e.cantidad)

    def _a_entidad(self, m: StockModel) -> Stock:
        """Convierte el modelo SQL en su entidad."""
        return Stock(_libro_a_entidad(m.libro), m.cantidad)

    def leer_por_id(self, id: int) -> Optional[Stock]:
        """El stock se identifica por el ID de su libro."""
        return self.leer_por_libro(id)

    def leer_por_libro(self, libro_id: int) -> Optional[Stock]:
        """Busca el stock de un libro.

        Args:
            libro_id (int): ID del libro.

        Returns:
            Optional[Stock]: El stock, o None si el libro no tiene.
        """
        with self.db.obtener_sesion() as sesion:
            m = sesion.get(StockModel, libro_id)
            return self._a_entidad(m) if m else None

    def eliminar(self, libro_id: int) -> bool:
        """Elimina el stock de un libro.

        Args:
            libro_id (int): ID del libro.

        Returns:
            bool: True si se eliminó, False si no existía.
        """
        with self.db.obtener_sesion() as sesion:
            m = sesion.get(StockModel, libro_id)
            if m:
                sesion.delete(m)
                return True
            return False


class RepositorioCotizacionDolar(RepositorioBase[CotizacionDolar],
                                 IRepositorioCotizacionDolar):
    """Repositorio de cotizaciones del dólar (clave: tipo + fecha)."""

    def __init__(self, db: ConexionDB) -> None:
        """Indica el modelo SQL con el que trabaja el repositorio."""
        super().__init__(db, CotizacionDolarModel)

    def _a_modelo(self, e: CotizacionDolar) -> CotizacionDolarModel:
        """Convierte la entidad en su modelo SQL."""
        return CotizacionDolarModel(tipo_id=e.tipo.id, fecha=e.fecha,
                                    compra=e.compra, venta=e.venta)

    def _a_entidad(self, m: CotizacionDolarModel) -> CotizacionDolar:
        """Convierte el modelo SQL en su entidad."""
        tipo = TipoCotizacion(m.tipo.id, m.tipo.nombre)
        return CotizacionDolar(tipo, m.fecha, m.compra, m.venta)

    def leer_por_tipo_y_fecha(
        self, tipo_id: int, fecha: datetime.date
    ) -> Optional[CotizacionDolar]:
        """Busca la cotización de un tipo en una fecha.

        Args:
            tipo_id (int): ID del tipo de cotización.
            fecha (datetime.date): Fecha de la cotización.

        Returns:
            Optional[CotizacionDolar]: La cotización, o None si no hay.
        """
        with self.db.obtener_sesion() as sesion:
            m = sesion.get(CotizacionDolarModel, (tipo_id, fecha))
            return self._a_entidad(m) if m else None

    def leer_historico_por_tipo(self, tipo_id: int) -> List[CotizacionDolar]:
        """Devuelve las cotizaciones de un tipo, de la más vieja a la más
        nueva.

        Args:
            tipo_id (int): ID del tipo de cotización.

        Returns:
            List[CotizacionDolar]: El histórico ordenado por fecha.
        """
        with self.db.obtener_sesion() as sesion:
            modelos = (
                sesion.query(CotizacionDolarModel)
                .filter(CotizacionDolarModel.tipo_id == tipo_id)
                .order_by(CotizacionDolarModel.fecha)
                .all()
            )
            return [self._a_entidad(m) for m in modelos]

    def eliminar(self, tipo_id: int, fecha: datetime.date) -> bool:
        """Elimina la cotización de un tipo en una fecha.

        Args:
            tipo_id (int): ID del tipo de cotización.
            fecha (datetime.date): Fecha de la cotización.

        Returns:
            bool: True si se eliminó, False si no existía.
        """
        with self.db.obtener_sesion() as sesion:
            m = sesion.get(CotizacionDolarModel, (tipo_id, fecha))
            if m:
                sesion.delete(m)
                return True
            return False
class RepositorioPrecioWeb(IRepositorioPrecioWeb):
    """Repositorio de los precios extraídos de la web."""

    def __init__(self, db: ConexionDB) -> None:
        """Guarda la conexión a la base de datos."""
        self.db = db

    def leer_ultimas(self) -> List[PrecioWeb]:
        """Lee, para cada libro, los precios de su extracción más reciente.

        Returns:
            List[PrecioWeb]: Los precios web de la última extracción de
            cada libro del catálogo.
        """
        with self.db.obtener_sesion() as sesion:
            ultimas = (
                sesion.query(
                    PrecioWebModel.libro_id,
                    func.max(PrecioWebModel.fecha_extraccion).label("fecha"),
                )
                .group_by(PrecioWebModel.libro_id)
                .subquery()
            )
            modelos = (
                sesion.query(PrecioWebModel)
                .join(ultimas, and_(
                    PrecioWebModel.libro_id == ultimas.c.libro_id,
                    PrecioWebModel.fecha_extraccion == ultimas.c.fecha,
                ))
                .all()
            )
            return [self._a_entidad(m) for m in modelos]

    @staticmethod
    def _a_entidad(m: PrecioWebModel) -> PrecioWeb:
        """Convierte el modelo SQL en su entidad."""
        return PrecioWeb(
            libro_id=m.libro_id, titulo_web=m.titulo_web, precio=m.precio,
            url_detalle=m.url_detalle, fecha_extraccion=m.fecha_extraccion,
            isbn=m.isbn, precio_usd=m.precio_usd, url_imagen=m.url_imagen,
            formas_pago=m.formas_pago, descripcion=m.descripcion,
        )