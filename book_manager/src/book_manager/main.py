"""Punto de entrada del gestor de libros."""

from pathlib import Path

from .database.connection import ConexionDB
from .migrations.migrations import migrar_datos
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


def main(import_default_data: bool = True) -> None:
    """Inicia el sistema, migra los datos y abre la consola.

    Args:
        import_default_data (bool): Si es True se migran los CSV de
            migrations/csv a la base antes de abrir el menú.
    """
    db = ConexionDB()

    if import_default_data:
        ruta_base = Path(__file__).parent
        carpeta_csvs = ruta_base / "migrations" / "csv"
        carpeta_sqls = ruta_base / "migrations" / "sql"
        migrar_datos(str(carpeta_csvs), str(carpeta_sqls), db)

    crear_consola(db).ejecutar()


if __name__ == "__main__":
    main()
