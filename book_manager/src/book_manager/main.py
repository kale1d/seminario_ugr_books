"""Punto de entrada del gestor de libros."""

from pathlib import Path

from .preload_data.preload_data import importar_datos
from .repositories import (BaseDeDatos, RepositorioCotizacionDolar,
                           RepositorioEditorial, RepositorioGenero,
                           RepositorioLibro, RepositorioMoneda,
                           RepositorioPrecio, RepositorioStock,
                           RepositorioTipoCotizacion)
from .services import (ServicioCotizacionDolar, ServicioEditorial,
                       ServicioGenero, ServicioLibro, ServicioMoneda,
                       ServicioPrecio, ServicioStock, ServicioTipoCotizacion)
from .ui.console import Consola

# La base queda en book_manager/datos, sin importar desde dónde se ejecute
RUTA_BASE = Path(__file__).parents[2] / "datos" / "book_manager.sqlite3"


def crear_consola(base: BaseDeDatos) -> Consola:
    """Arma los repositorios y servicios sobre la base y se los pasa a la
    consola."""
    repo_generos = RepositorioGenero(base)
    repo_editoriales = RepositorioEditorial(base)
    repo_monedas = RepositorioMoneda(base)
    repo_tipos = RepositorioTipoCotizacion(base)
    repo_libros = RepositorioLibro(base)

    cotizaciones = ServicioCotizacionDolar(RepositorioCotizacionDolar(base),
                                           repo_tipos)
    return Consola(
        generos=ServicioGenero(repo_generos),
        editoriales=ServicioEditorial(repo_editoriales),
        monedas=ServicioMoneda(repo_monedas),
        tipos_cotizacion=ServicioTipoCotizacion(repo_tipos),
        libros=ServicioLibro(repo_libros, repo_editoriales, repo_generos),
        precios=ServicioPrecio(RepositorioPrecio(base), repo_libros,
                               repo_monedas, cotizaciones),
        stock=ServicioStock(RepositorioStock(base), repo_libros),
        cotizaciones=cotizaciones,
    )


def main(import_default_data: bool = True) -> None:
    """Abre la base, carga los datos de los CSV si se pide y muestra el
    menú principal.

    Args:
        import_default_data (bool): Si es True se importan los CSV de
            migrations/csv antes de abrir el menú.
    """
    with BaseDeDatos(RUTA_BASE) as base:
        if import_default_data:
            importar_datos(base)
        crear_consola(base).ejecutar()


if __name__ == "__main__":
    main()
