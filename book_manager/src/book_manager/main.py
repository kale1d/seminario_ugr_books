from pathlib import Path

# Importamos nuestra nueva conexión y el script de migración del Sprint 2
from .database.connection import ConexionDB
from .migrations.migrations import migrar_datos

# Importamos desde los archivos directamente para evitar conflictos con archivos viejos
from .repositories.repositories import (
    RepositorioCotizacionDolar, RepositorioEditorial, RepositorioGenero,
    RepositorioLibro, RepositorioMoneda, RepositorioPrecio,
    RepositorioStock, RepositorioTipoCotizacion
)
from .services.services import (
    ServicioCotizacionDolar, ServicioEditorial, ServicioGenero,
    ServicioLibro, ServicioMoneda, ServicioPrecio,
    ServicioStock, ServicioTipoCotizacion
)
from .ui.console import Consola

def crear_consola(db: ConexionDB) -> Consola:
    """Arma los repositorios y servicios conectándolos a SQLAlchemy."""
    repo_generos = RepositorioGenero(db)
    repo_editoriales = RepositorioEditorial(db)
    repo_monedas = RepositorioMoneda(db)
    repo_tipos = RepositorioTipoCotizacion(db)
    repo_libros = RepositorioLibro(db)
    
    cotizaciones = ServicioCotizacionDolar(RepositorioCotizacionDolar(db), repo_tipos)
    
    return Consola(
        generos=ServicioGenero(repo_generos),
        editoriales=ServicioEditorial(repo_editoriales),
        monedas=ServicioMoneda(repo_monedas),
        tipos_cotizacion=ServicioTipoCotizacion(repo_tipos),
        libros=ServicioLibro(repo_libros, repo_editoriales, repo_generos),
        precios=ServicioPrecio(RepositorioPrecio(db), repo_libros, repo_monedas, cotizaciones),
        stock=ServicioStock(RepositorioStock(db), repo_libros),
        cotizaciones=cotizaciones,
    )

def main(ejecutar_migracion: bool = True) -> None:
    """Inicia el sistema, migra los datos y abre la consola."""
    # 1. Iniciamos nuestra conexión a la base de datos
    db = ConexionDB()
    
    if ejecutar_migracion:
        # 2. Definimos las rutas dinámicas a nuestras carpetas de migración
        ruta_base = Path(__file__).parent
        carpeta_csvs = ruta_base / "migrations" / "csv"
        carpeta_sqls = ruta_base / "migrations" / "sql"
        
        # 3. Ejecutamos el script de migración del Ejercicio 05
        migrar_datos(str(carpeta_csvs), str(carpeta_sqls), db)
        
    # 4. Abrimos el menú principal
    crear_consola(db).ejecutar()

if __name__ == "__main__":
    main()