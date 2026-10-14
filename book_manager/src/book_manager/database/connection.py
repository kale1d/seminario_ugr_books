from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

Base = declarative_base()

class ConexionDB:
    """Maneja la conexión a la base de datos usando SQLAlchemy."""
    
    def __init__(self, db_url: str = "sqlite:///datos/book_manager.sqlite3"):
        self.engine = create_engine(db_url, echo=False)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    def crear_tablas(self):
        """Crea las tablas en la base de datos si no existen."""
        Base.metadata.create_all(bind=self.engine)