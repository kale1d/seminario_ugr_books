"""Migración de datos: de archivos CSV a archivos SQL y de ahí a la base."""

import csv
import os

from sqlalchemy import text

from ..database.connection import ConexionDB

# Archivo CSV de origen -> tabla destino. El orden importa: cada tabla se
# carga después de las que referencia por clave foránea (por ejemplo,
# los libros después de géneros y editoriales).
ARCHIVOS_TABLAS = {
    "generos.csv": "generos",
    "editoriales.csv": "editoriales",
    "tipos_cotizacion.csv": "tipos_cotizacion",
    "monedas.csv": "monedas",
    "libros.csv": "libros",
    "precios.csv": "precios",
    "stock.csv": "stock",
    "cotizaciones_dolar.csv": "cotizaciones_dolar",
}


def _literal_sql(valor: str) -> str:
    """Devuelve el valor como texto SQL entre comillas simples, duplicando
    las comillas que tenga adentro para que no rompan la sentencia."""
    comilla_doble = "''"
    return "'" + str(valor).replace("'", comilla_doble) + "'"


def generar_sqls(carpeta_csvs: str, carpeta_sqls: str) -> None:
    """Genera un archivo .sql por tabla a partir de los CSV.

    Cada fila del CSV se convierte en una sentencia INSERT escrita en su
    propia línea.

    Args:
        carpeta_csvs (str): Carpeta donde están los archivos CSV.
        carpeta_sqls (str): Carpeta donde se guardan los .sql generados.
    """
    os.makedirs(carpeta_sqls, exist_ok=True)

    for archivo_csv, tabla in ARCHIVOS_TABLAS.items():
        ruta_csv = os.path.join(carpeta_csvs, archivo_csv)
        ruta_sql = os.path.join(carpeta_sqls, f"{tabla}.sql")

        if not os.path.exists(ruta_csv):
            print(f"No se encontró el archivo {archivo_csv}, saltando...")
            continue

        with open(ruta_csv, mode="r", encoding="utf-8") as f_csv, \
                open(ruta_sql, mode="w", encoding="utf-8") as f_sql:
            for fila in csv.DictReader(f_csv):
                columnas = ", ".join(fila.keys())
                valores = ", ".join(_literal_sql(v) for v in fila.values())
                # ON CONFLICT DO NOTHING permite volver a cargar el archivo
                # sin errores si los datos ya existen.
                f_sql.write(
                    f"INSERT INTO {tabla} ({columnas}) VALUES ({valores}) "
                    f"ON CONFLICT DO NOTHING;\n"
                )


def cargar_datos_desde_sql(carpeta_sqls: str, db: ConexionDB) -> None:
    """Ejecuta en la base de datos las sentencias de los archivos .sql.

    Los archivos se cargan en el orden de ARCHIVOS_TABLAS, todos dentro de
    una misma transacción: si alguna sentencia falla, no se guarda nada.

    Args:
        carpeta_sqls (str): Carpeta donde están los archivos .sql.
        db (ConexionDB): Conexión a la base de datos.
    """
    db.crear_tablas()

    with db.obtener_sesion() as sesion:
        for tabla in ARCHIVOS_TABLAS.values():
            ruta_sql = os.path.join(carpeta_sqls, f"{tabla}.sql")

            if not os.path.exists(ruta_sql):
                print(f"No se encontró {tabla}.sql, saltando...")
                continue

            with open(ruta_sql, mode="r", encoding="utf-8") as f_sql:
                for linea in f_sql:
                    sentencia = linea.strip()
                    if sentencia:
                        sesion.execute(text(sentencia))


def migrar_datos(carpeta_csvs: str, carpeta_sqls: str,
                 db: ConexionDB = None) -> None:
    """Migra los datos de los CSV a la base de datos.

    Genera los archivos .sql a partir de los CSV y luego los carga.

    Args:
        carpeta_csvs (str): Carpeta donde están los archivos CSV de origen.
        carpeta_sqls (str): Carpeta donde se guardan los .sql generados.
        db (ConexionDB): Conexión a usar; si no se pasa, se crea una.
    """
    if db is None:
        db = ConexionDB()

    generar_sqls(carpeta_csvs, carpeta_sqls)
    cargar_datos_desde_sql(carpeta_sqls, db)
    print("Migración a SQL completada con éxito.")