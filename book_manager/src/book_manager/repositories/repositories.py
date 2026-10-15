from typing import TypeVar, Generic, List, Optional
from ..database.connection import ConexionDB
from ..models.models import (
    GeneroModel, EditorialModel, MonedaModel, TipoCotizacionModel,
    LibroModel, PrecioModel, StockModel, CotizacionDolarModel
)
# Importamos las Entidades puras de tu Sprint 1
from ..entities.genero import Genero
from ..entities.editorial import Editorial
from ..entities.moneda import Moneda
from ..entities.tipo_cotizacion import TipoCotizacion
from ..entities.libro import Libro
from ..entities.precio import Precio
from ..entities.stock import Stock
from ..entities.cotizacion_dolar import CotizacionDolar

T = TypeVar('T')

class RepositorioBase(Generic[T]):
    """Repositorio traductor: Convierte entre Entidades de Python y Modelos de Base de Datos."""
    
    def __init__(self, db: ConexionDB, modelo_cls: type):
        self.db = db
        self.modelo_cls = modelo_cls

    def _a_modelo(self, entidad: T):
        """Convierte una Entidad a un Modelo SQL (Debe implementarse en las hijas)"""
        raise NotImplementedError

    def _a_entidad(self, modelo) -> T:
        """Convierte un Modelo SQL a una Entidad (Debe implementarse en las hijas)"""
        raise NotImplementedError

    def crear(self, entidad: T) -> T:
        with self.db.obtener_sesion() as sesion:
            modelo = self._a_modelo(entidad)
            sesion.add(modelo)
            sesion.flush() # Guardamos en BD
            # Devolvemos la entidad original intacta, evitando errores de relaciones vacías
            return entidad

    def leer_por_id(self, id_entidad: int) -> Optional[T]:
        with self.db.obtener_sesion() as sesion:
            modelo = sesion.query(self.modelo_cls).filter(self.modelo_cls.id == id_entidad).first()
            return self._a_entidad(modelo) if modelo else None

    def leer_todos(self) -> List[T]:
        with self.db.obtener_sesion() as sesion:
            modelos = sesion.query(self.modelo_cls).all()
            return [self._a_entidad(m) for m in modelos]

    def actualizar(self, entidad: T) -> T:
        with self.db.obtener_sesion() as sesion:
            modelo = self._a_modelo(entidad)
            sesion.merge(modelo)
            return entidad

    def eliminar(self, id_entidad: int) -> bool:
        with self.db.obtener_sesion() as sesion:
            modelo = sesion.query(self.modelo_cls).filter(self.modelo_cls.id == id_entidad).first()
            if modelo:
                sesion.delete(modelo)
                return True
            return False

# --- Repositorios Específicos con sus Traductores ---

class RepositorioGenero(RepositorioBase[Genero]):
    def __init__(self, db: ConexionDB): super().__init__(db, GeneroModel)
    def _a_modelo(self, e: Genero): return GeneroModel(id=e.id, nombre=e.nombre)
    def _a_entidad(self, m: GeneroModel): return Genero(m.id, m.nombre)

class RepositorioEditorial(RepositorioBase[Editorial]):
    def __init__(self, db: ConexionDB): super().__init__(db, EditorialModel)
    def _a_modelo(self, e: Editorial): return EditorialModel(id=e.id, nombre=e.nombre)
    def _a_entidad(self, m: EditorialModel): return Editorial(m.id, m.nombre)

class RepositorioTipoCotizacion(RepositorioBase[TipoCotizacion]):
    def __init__(self, db: ConexionDB): super().__init__(db, TipoCotizacionModel)
    def _a_modelo(self, e: TipoCotizacion): return TipoCotizacionModel(id=e.id, nombre=e.nombre)
    def _a_entidad(self, m: TipoCotizacionModel): return TipoCotizacion(m.id, m.nombre)

class RepositorioMoneda(RepositorioBase[Moneda]):
    def __init__(self, db: ConexionDB): super().__init__(db, MonedaModel)
    def _a_modelo(self, e: Moneda): return MonedaModel(id=e.id, nombre=e.nombre, codigo=e.codigo)
    def _a_entidad(self, m: MonedaModel): return Moneda(m.id, m.nombre, m.codigo)

class RepositorioLibro(RepositorioBase[Libro]):
    def __init__(self, db: ConexionDB): super().__init__(db, LibroModel)
    def _a_modelo(self, e: Libro):
        return LibroModel(id=e.id, isbn=e.isbn, titulo=e.titulo, autor=e.autor, 
                          editorial_id=e.editorial.id, genero_id=e.genero.id)
    def _a_entidad(self, m: LibroModel):
        editorial = Editorial(m.editorial.id, m.editorial.nombre)
        genero = Genero(m.genero.id, m.genero.nombre)
        return Libro(m.id, m.isbn, m.titulo, m.autor, editorial, genero)

class RepositorioPrecio(RepositorioBase[Precio]):
    def __init__(self, db: ConexionDB): super().__init__(db, PrecioModel)
    def _a_modelo(self, e: Precio):
        return PrecioModel(id=e.id, valor=e.valor, libro_id=e.libro.id, moneda_id=e.moneda.id)
    def _a_entidad(self, m: PrecioModel):
        editorial = Editorial(m.libro.editorial.id, m.libro.editorial.nombre)
        genero = Genero(m.libro.genero.id, m.libro.genero.nombre)
        libro = Libro(m.libro.id, m.libro.isbn, m.libro.titulo, m.libro.autor, editorial, genero)
        moneda = Moneda(m.moneda.id, m.moneda.nombre, m.moneda.codigo)
        return Precio(m.id, libro, moneda, m.valor)

class RepositorioStock(RepositorioBase[Stock]):
    def __init__(self, db: ConexionDB): super().__init__(db, StockModel)
    def _a_modelo(self, e: Stock):
        return StockModel(libro_id=e.libro.id, cantidad=e.cantidad)
    def _a_entidad(self, m: StockModel):
        editorial = Editorial(m.libro.editorial.id, m.libro.editorial.nombre)
        genero = Genero(m.libro.genero.id, m.libro.genero.nombre)
        libro = Libro(m.libro.id, m.libro.isbn, m.libro.titulo, m.libro.autor, editorial, genero)
        return Stock(libro, m.cantidad)
        
    def leer_por_libro(self, libro_id: int) -> Optional[Stock]:
        with self.db.obtener_sesion() as sesion:
            m = sesion.query(StockModel).filter(StockModel.libro_id == libro_id).first()
            return self._a_entidad(m) if m else None

    def eliminar(self, libro_id: int) -> bool:
        with self.db.obtener_sesion() as sesion:
            m = sesion.query(StockModel).filter(StockModel.libro_id == libro_id).first()
            if m:
                sesion.delete(m)
                return True
            return False

class RepositorioCotizacionDolar(RepositorioBase[CotizacionDolar]):
    def __init__(self, db: ConexionDB): super().__init__(db, CotizacionDolarModel)
    def _a_modelo(self, e: CotizacionDolar):
        return CotizacionDolarModel(tipo_id=e.tipo.id, fecha=e.fecha, compra=e.compra, venta=e.venta)
    def _a_entidad(self, m: CotizacionDolarModel):
        tipo = TipoCotizacion(m.tipo.id, m.tipo.nombre)
        return CotizacionDolar(tipo, m.fecha, m.compra, m.venta)

    def leer_por_tipo_y_fecha(self, tipo_id: int, fecha) -> Optional[CotizacionDolar]:
        with self.db.obtener_sesion() as sesion:
            m = sesion.query(CotizacionDolarModel).filter(
                CotizacionDolarModel.tipo_id == tipo_id,
                CotizacionDolarModel.fecha == fecha
            ).first()
            return self._a_entidad(m) if m else None

    def leer_historico_por_tipo(self, tipo_id: int) -> List[CotizacionDolar]:
        with self.db.obtener_sesion() as sesion:
            modelos = sesion.query(CotizacionDolarModel).filter(CotizacionDolarModel.tipo_id == tipo_id).all()
            return [self._a_entidad(m) for m in modelos]

    def eliminar(self, tipo_id: int, fecha) -> bool:
        with self.db.obtener_sesion() as sesion:
            m = sesion.query(CotizacionDolarModel).filter(
                CotizacionDolarModel.tipo_id == tipo_id,
                CotizacionDolarModel.fecha == fecha
            ).first()
            if m:
                sesion.delete(m)
                return True
            return False