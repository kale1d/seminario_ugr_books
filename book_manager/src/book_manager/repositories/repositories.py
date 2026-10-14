from typing import TypeVar, Generic, List, Optional
from ..database.connection import ConexionDB
from ..models.models import (
    GeneroModel, EditorialModel, MonedaModel, TipoCotizacionModel,
    LibroModel, PrecioModel, StockModel, CotizacionDolarModel
)

T = TypeVar('T')

class RepositorioBase(Generic[T]):
    """Repositorio genérico con las operaciones CRUD básicas usando SQLAlchemy."""
    
    def __init__(self, db: ConexionDB, modelo: type):
        self.db = db
        self.modelo = modelo

    def crear(self, entidad: T) -> T:
        with self.db.obtener_sesion() as sesion:
            sesion.add(entidad)
            sesion.commit()
            sesion.refresh(entidad)
            return entidad

    def leer_por_id(self, id_entidad: int) -> Optional[T]:
        with self.db.obtener_sesion() as sesion:
            return sesion.query(self.modelo).filter(self.modelo.id == id_entidad).first()

    def leer_todos(self) -> List[T]:
        with self.db.obtener_sesion() as sesion:
            return sesion.query(self.modelo).all()

    def actualizar(self, entidad: T) -> T:
        with self.db.obtener_sesion() as sesion:
            # merge une los datos nuevos con los existentes en la base de datos
            entidad_actualizada = sesion.merge(entidad)
            sesion.commit()
            return entidad_actualizada

    def eliminar(self, id_entidad: int) -> bool:
        with self.db.obtener_sesion() as sesion:
            entidad = sesion.query(self.modelo).filter(self.modelo.id == id_entidad).first()
            if entidad:
                sesion.delete(entidad)
                sesion.commit()
                return True
            return False

# --- Repositorios Específicos ---

class RepositorioGenero(RepositorioBase[GeneroModel]):
    def __init__(self, db: ConexionDB):
        super().__init__(db, GeneroModel)

class RepositorioEditorial(RepositorioBase[EditorialModel]):
    def __init__(self, db: ConexionDB):
        super().__init__(db, EditorialModel)

class RepositorioMoneda(RepositorioBase[MonedaModel]):
    def __init__(self, db: ConexionDB):
        super().__init__(db, MonedaModel)

class RepositorioTipoCotizacion(RepositorioBase[TipoCotizacionModel]):
    def __init__(self, db: ConexionDB):
        super().__init__(db, TipoCotizacionModel)

class RepositorioLibro(RepositorioBase[LibroModel]):
    def __init__(self, db: ConexionDB):
        super().__init__(db, LibroModel)

class RepositorioPrecio(RepositorioBase[PrecioModel]):
    def __init__(self, db: ConexionDB):
        super().__init__(db, PrecioModel)

class RepositorioStock(RepositorioBase[StockModel]):
    def __init__(self, db: ConexionDB):
        super().__init__(db, StockModel)

    def leer_por_libro(self, libro_id: int) -> Optional[StockModel]:
        with self.db.obtener_sesion() as sesion:
            return sesion.query(StockModel).filter(StockModel.libro_id == libro_id).first()

    def eliminar(self, libro_id: int) -> bool:
        with self.db.obtener_sesion() as sesion:
            entidad = sesion.query(StockModel).filter(StockModel.libro_id == libro_id).first()
            if entidad:
                sesion.delete(entidad)
                sesion.commit()
                return True
            return False

class RepositorioCotizacionDolar(RepositorioBase[CotizacionDolarModel]):
    def __init__(self, db: ConexionDB):
        super().__init__(db, CotizacionDolarModel)

    def leer_por_tipo_y_fecha(self, tipo_id: int, fecha) -> Optional[CotizacionDolarModel]:
        with self.db.obtener_sesion() as sesion:
            return sesion.query(CotizacionDolarModel).filter(
                CotizacionDolarModel.tipo_id == tipo_id,
                CotizacionDolarModel.fecha == fecha
            ).first()

    def leer_historico_por_tipo(self, tipo_id: int) -> List[CotizacionDolarModel]:
        with self.db.obtener_sesion() as sesion:
            return sesion.query(CotizacionDolarModel).filter(CotizacionDolarModel.tipo_id == tipo_id).all()

    def eliminar(self, tipo_id: int, fecha) -> bool:
        with self.db.obtener_sesion() as sesion:
            entidad = sesion.query(CotizacionDolarModel).filter(
                CotizacionDolarModel.tipo_id == tipo_id,
                CotizacionDolarModel.fecha == fecha
            ).first()
            if entidad:
                sesion.delete(entidad)
                sesion.commit()
                return True
            return False
