from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from contextlib import contextmanager

Base = declarative_base()

class ConexionDB:
    """Maneja la conexión a la base de datos usando SQLAlchemy."""
    
    def __init__(self, db_url: str = "sqlite:///datos/book_manager.sqlite3"):
        self.engine = create_engine(db_url, echo=False)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    def crear_tablas(self):
        """Crea las tablas en la base de datos si no existen."""
        Base.metadata.create_all(bind=self.engine)

    @contextmanager
    def obtener_sesion(self):
        """
        Context manager para manejar las transacciones a la base de datos.
        Asegura que la sesión se cierre correctamente y maneja errores.
        """
        sesion = self.SessionLocal()
        try:
            yield sesion
            sesion.commit()
        except Exception as e:
            sesion.rollback()
            raise e
        finally:
            sesion.close()