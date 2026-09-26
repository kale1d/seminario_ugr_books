"""Carga inicial de datos del gestor de libros.

Lee los archivos CSV de migrations/csv y los guarda en la base usando los
servicios, así los datos pasan por las mismas validaciones que el resto
del sistema.
"""

import csv
from datetime import date
from pathlib import Path
from typing import Dict, List

from ..entities import (CotizacionDolar, Editorial, Genero, Libro, Moneda,
                        Precio, Stock, TipoCotizacion)
from ..repositories import (BaseDeDatos, RepositorioCotizacionDolar,
                            RepositorioEditorial, RepositorioGenero,
                            RepositorioLibro, RepositorioMoneda,
                            RepositorioPrecio, RepositorioStock,
                            RepositorioTipoCotizacion)
from ..services import (ServicioCotizacionDolar, ServicioEditorial,
                        ServicioGenero, ServicioLibro, ServicioMoneda,
                        ServicioPrecio, ServicioStock, ServicioTipoCotizacion)

CARPETA_CSV = Path(__file__).parent.parent / "migrations" / "csv"


def leer_csv(nombre: str) -> List[Dict[str, str]]:
    """Devuelve las filas de un CSV de la carpeta de migraciones como
    diccionarios (columna -> valor)."""
    with open(CARPETA_CSV / nombre, encoding="utf-8", newline="") as archivo:
        return list(csv.DictReader(archivo))


def importar_datos(base: BaseDeDatos) -> None:
    """Carga todos los CSV en la base.

    Se cargan en orden para que cada registro encuentre lo que referencia
    (por ejemplo, las editoriales y los géneros antes que los libros).
    Los registros que ya existen se saltean, así que se puede correr más
    de una vez sin que falle.
    """
    repo_generos = RepositorioGenero(base)
    repo_editoriales = RepositorioEditorial(base)
    repo_monedas = RepositorioMoneda(base)
    repo_tipos = RepositorioTipoCotizacion(base)
    repo_libros = RepositorioLibro(base)

    generos = ServicioGenero(repo_generos)
    editoriales = ServicioEditorial(repo_editoriales)
    monedas = ServicioMoneda(repo_monedas)
    tipos = ServicioTipoCotizacion(repo_tipos)
    libros = ServicioLibro(repo_libros, repo_editoriales, repo_generos)
    cotizaciones = ServicioCotizacionDolar(
        RepositorioCotizacionDolar(base), repo_tipos
    )
    precios = ServicioPrecio(RepositorioPrecio(base), repo_libros,
                             repo_monedas, cotizaciones)
    stock = ServicioStock(RepositorioStock(base), repo_libros)

    for fila in leer_csv("generos.csv"):
        if generos.leer_por_id(int(fila["id"])) is None:
            generos.crear(Genero(int(fila["id"]), fila["nombre"]))

    for fila in leer_csv("editoriales.csv"):
        if editoriales.leer_por_id(int(fila["id"])) is None:
            editoriales.crear(Editorial(int(fila["id"]), fila["nombre"]))

    for fila in leer_csv("monedas.csv"):
        if monedas.leer_por_id(int(fila["id"])) is None:
            monedas.crear(
                Moneda(int(fila["id"]), fila["nombre"], fila["codigo"])
            )

    for fila in leer_csv("tipos_cotizacion.csv"):
        if tipos.leer_por_id(int(fila["id"])) is None:
            tipos.crear(TipoCotizacion(int(fila["id"]), fila["nombre"]))

    # Diccionarios por ID para armar las relaciones de los libros
    por_id_editorial = {e.id: e for e in editoriales.leer_todos()}
    por_id_genero = {g.id: g for g in generos.leer_todos()}
    for fila in leer_csv("libros.csv"):
        if libros.leer_por_id(int(fila["id"])) is None:
            libros.crear(Libro(
                int(fila["id"]), fila["isbn"], fila["titulo"], fila["autor"],
                por_id_editorial[int(fila["editorial_id"])],
                por_id_genero[int(fila["genero_id"])],
            ))

    por_id_libro = {libro.id: libro for libro in libros.leer_todos()}
    por_id_moneda = {m.id: m for m in monedas.leer_todos()}
    for fila in leer_csv("precios.csv"):
        if precios.leer_por_id(int(fila["id"])) is None:
            precios.crear(Precio(
                int(fila["id"]),
                por_id_libro[int(fila["libro_id"])],
                por_id_moneda[int(fila["moneda_id"])],
                fila["valor"],
            ))

    for fila in leer_csv("stock.csv"):
        libro_id = int(fila["libro_id"])
        if stock.leer_por_libro(libro_id) is None:
            stock.crear(Stock(por_id_libro[libro_id], int(fila["cantidad"])))

    por_id_tipo = {t.id: t for t in tipos.leer_todos()}
    for fila in leer_csv("cotizaciones_dolar.csv"):
        tipo_id = int(fila["tipo_id"])
        fecha = date.fromisoformat(fila["fecha"])
        if cotizaciones.leer_por_tipo_y_fecha(tipo_id, fecha) is None:
            cotizaciones.crear(CotizacionDolar(
                por_id_tipo[tipo_id], fecha, fila["compra"], fila["venta"]
            ))


if __name__ == "__main__":
    with BaseDeDatos() as base_de_datos:
        importar_datos(base_de_datos)
        print("Datos importados correctamente.")
