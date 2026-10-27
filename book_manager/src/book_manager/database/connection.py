"""Conexión a la base de datos con SQLAlchemy."""

import os
from dotenv import load_dotenv
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv()

Base = declarative_base()

class ConexionDB:
    """Maneja la conexión a la base de datos usando SQLAlchemy."""
    
    def __init__(self):
        """Lee DATABASE_URL del .env y crea el motor y la fábrica de sesiones."""
        db_url = os.getenv("DATABASE_URL")
        
        if not db_url:
            raise ValueError("No se encontró DATABASE_URL en el archivo .env")
            
        if db_url.startswith("postgres://"):
            db_url = db_url.replace("postgres://", "postgresql+psycopg2://", 1)
        elif db_url.startswith("postgresql://"):
            db_url = db_url.replace("postgresql://", "postgresql+psycopg2://", 1)
            
        self.engine = create_engine(db_url, echo=False)
        
        # AGREGADO: expire_on_commit=False evita el DetachedInstanceError
        self.SessionLocal = sessionmaker(
            autocommit=False, 
            autoflush=False, 
            bind=self.engine,
            expire_on_commit=False 
        )

    def crear_tablas(self):
        """Crea las tablas en la base de datos si no existen."""
        Base.metadata.create_all(bind=self.engine)

    @contextmanager
    def obtener_sesion(self):
        """Context manager para manejar las transacciones a la base de datos."""
        sesion = self.SessionLocal()
        try:
            yield sesion
            sesion.commit()
        except Exception as e:
            sesion.rollback()
            raise e
        finally:
            sesion.close()