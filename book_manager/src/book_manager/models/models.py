"""Modelos SQLAlchemy: tablas de la base de datos y sus relaciones.

Cada modelo representa una tabla. Las relaciones se declaran en ambos
sentidos con ``back_populates`` (por ejemplo, un libro conoce a su
editorial y una editorial conoce a sus libros).
"""

from sqlalchemy import (
    JSON, Column, Date, DateTime, ForeignKey, Integer, Numeric, 
    String, Text
    )
from sqlalchemy.orm import relationship

from ..database.connection import Base

# --- Entidades básicas ---


class GeneroModel(Base):
    """Tabla de géneros literarios."""

    __tablename__ = "generos"

    id = Column(Integer, primary_key=True)
    nombre = Column(String, nullable=False)

    # passive_deletes="all": el ORM no toca los hijos al borrar el padre,
    # así la base rechaza el borrado de un registro que está en uso.
    libros = relationship("LibroModel", back_populates="genero",
                          passive_deletes="all")


class EditorialModel(Base):
    """Tabla de editoriales."""

    __tablename__ = "editoriales"

    id = Column(Integer, primary_key=True)
    nombre = Column(String, nullable=False)

    libros = relationship("LibroModel", back_populates="editorial",
                          passive_deletes="all")


class MonedaModel(Base):
    """Tabla de monedas (el código es único, por ejemplo ARS o USD)."""

    __tablename__ = "monedas"

    id = Column(Integer, primary_key=True)
    nombre = Column(String, nullable=False)
    codigo = Column(String, nullable=False, unique=True)

    precios = relationship("PrecioModel", back_populates="moneda",
                           passive_deletes="all")


class TipoCotizacionModel(Base):
    """Tabla de tipos de cotización del dólar (oficial, blue, etc.)."""

    __tablename__ = "tipos_cotizacion"

    id = Column(Integer, primary_key=True)
    nombre = Column(String, nullable=False)

    cotizaciones = relationship("CotizacionDolarModel",
                                back_populates="tipo",
                                passive_deletes="all")


# --- Entidades con relaciones ---


class LibroModel(Base):
    """Tabla de libros, con su editorial y su género."""

    __tablename__ = "libros"

    id = Column(Integer, primary_key=True)
    isbn = Column(String, nullable=False, unique=True)
    titulo = Column(String, nullable=False)
    autor = Column(String, nullable=False)

    editorial_id = Column(Integer, ForeignKey("editoriales.id"))
    genero_id = Column(Integer, ForeignKey("generos.id"))

    # lazy="joined" trae la relación en la misma consulta y evita errores
    # al usar el modelo después de cerrar la sesión.
    editorial = relationship("EditorialModel", back_populates="libros",
                             lazy="joined")
    genero = relationship("GeneroModel", back_populates="libros",
                          lazy="joined")
    precios = relationship("PrecioModel", back_populates="libro",
                           passive_deletes="all")
    stock = relationship("StockModel", back_populates="libro",
                         uselist=False, passive_deletes="all")
    precios_web = relationship("PrecioWebModel", back_populates="libro",
                               passive_deletes="all")


class PrecioModel(Base):
    """Tabla de precios: valor de un libro en una moneda."""

    __tablename__ = "precios"

    id = Column(Integer, primary_key=True)
    valor = Column(Numeric(10, 2), nullable=False)

    libro_id = Column(Integer, ForeignKey("libros.id"))
    moneda_id = Column(Integer, ForeignKey("monedas.id"))

    libro = relationship("LibroModel", back_populates="precios",
                         lazy="joined")
    moneda = relationship("MonedaModel", back_populates="precios",
                          lazy="joined")


class StockModel(Base):
    """Tabla de stock: unidades disponibles de cada libro."""

    __tablename__ = "stock"

    libro_id = Column(Integer, ForeignKey("libros.id"), primary_key=True)
    cantidad = Column(Integer, nullable=False, default=0)

    libro = relationship("LibroModel", back_populates="stock",
                         lazy="joined")


class CotizacionDolarModel(Base):
    """Tabla del histórico de cotizaciones (clave: tipo + fecha)."""

    __tablename__ = "cotizaciones_dolar"

    tipo_id = Column(Integer, ForeignKey("tipos_cotizacion.id"),
                     primary_key=True)
    fecha = Column(Date, primary_key=True)
    compra = Column(Numeric(10, 2), nullable=False)
    venta = Column(Numeric(10, 2), nullable=False)

    tipo = relationship("TipoCotizacionModel",
                        back_populates="cotizaciones", lazy="joined")
class PrecioWebModel(Base):
    """Tabla de precios obtenidos de la web (Cúspide) en cada extracción."""

    __tablename__ = "precios_web"

    id = Column(Integer, primary_key=True)
    libro_id = Column(Integer, ForeignKey("libros.id"), nullable=False)
    titulo_web = Column(String)
    isbn = Column(String)
    precio = Column(Numeric(12, 2), nullable=False)
    precio_usd = Column(Numeric(10, 2))
    url_imagen = Column(String)
    formas_pago = Column(JSON)
    descripcion = Column(Text)
    url_detalle = Column(String, nullable=False)
    fecha_extraccion = Column(DateTime, nullable=False)

    libro = relationship("LibroModel", back_populates="precios_web",
                         lazy="joined")


class AuditoriaModel(Base):
    """Tabla del historial de auditoría: qué se hizo y cuándo."""

    __tablename__ = "auditoria"

    id = Column(Integer, primary_key=True)
    accion = Column(String, nullable=False)
    fecha = Column(DateTime, nullable=False)
    detalles = Column(Text)
