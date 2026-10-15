from sqlalchemy import Column, Integer, String, Numeric, Date, ForeignKey
from sqlalchemy.orm import relationship
# Importamos la Base que creaste en el Ejercicio 02
from ..database.connection import Base

# --- Entidades Básicas ---

class GeneroModel(Base):
    __tablename__ = "generos"
    id = Column(Integer, primary_key=True)
    nombre = Column(String, nullable=False)

class EditorialModel(Base):
    __tablename__ = "editoriales"
    id = Column(Integer, primary_key=True)
    nombre = Column(String, nullable=False)

class MonedaModel(Base):
    __tablename__ = "monedas"
    id = Column(Integer, primary_key=True)
    nombre = Column(String, nullable=False)
    codigo = Column(String, nullable=False, unique=True)

class TipoCotizacionModel(Base):
    __tablename__ = "tipos_cotizacion"
    id = Column(Integer, primary_key=True)
    nombre = Column(String, nullable=False)

# --- Entidades con Relaciones ---
# --- Entidades con Relaciones ---

class LibroModel(Base):
    __tablename__ = "libros"
    id = Column(Integer, primary_key=True)
    isbn = Column(String, nullable=False, unique=True)
    titulo = Column(String, nullable=False)
    autor = Column(String, nullable=False)
    
    editorial_id = Column(Integer, ForeignKey("editoriales.id"))
    genero_id = Column(Integer, ForeignKey("generos.id"))

    # Agregamos lazy="joined" a todas las relaciones
    editorial = relationship("EditorialModel", lazy="joined")
    genero = relationship("GeneroModel", lazy="joined")

class PrecioModel(Base):
    __tablename__ = "precios"
    id = Column(Integer, primary_key=True)
    valor = Column(Numeric(10, 2), nullable=False) 
    
    libro_id = Column(Integer, ForeignKey("libros.id"))
    moneda_id = Column(Integer, ForeignKey("monedas.id"))
    
    libro = relationship("LibroModel", lazy="joined")
    moneda = relationship("MonedaModel", lazy="joined")

class StockModel(Base):
    __tablename__ = "stock"
    libro_id = Column(Integer, ForeignKey("libros.id"), primary_key=True)
    cantidad = Column(Integer, nullable=False, default=0)
    
    libro = relationship("LibroModel", lazy="joined")

class CotizacionDolarModel(Base):
    __tablename__ = "cotizaciones_dolar"
    tipo_id = Column(Integer, ForeignKey("tipos_cotizacion.id"), primary_key=True)
    fecha = Column(Date, primary_key=True)
    compra = Column(Numeric(10, 2), nullable=False)
    venta = Column(Numeric(10, 2), nullable=False)
    
    tipo = relationship("TipoCotizacionModel", lazy="joined")