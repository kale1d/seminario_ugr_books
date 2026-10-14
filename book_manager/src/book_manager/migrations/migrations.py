import csv
import os
from sqlalchemy import text
from ..database.connection import ConexionDB

def migrar_datos(carpeta_csvs: str, carpeta_sqls: str):
    """ Función encargada de la migración de datos de csv a sql.
    Se encarga de leer los archivos csv y crear los archivos sql
    para la inserción en la base de datos.

    Args:
        carpeta_csvs (str): Carpeta donde se encuentran los archivos csv de origen.
        carpeta_sqls (str): Carpeta donde se deben guardar los archivos sql generados.
    """
    # 1. Nos aseguramos de que la carpeta para guardar los SQL exista
    os.makedirs(carpeta_sqls, exist_ok=True)
    
    # 2. Relacionamos el nombre de cada archivo CSV con el nombre de su tabla
    archivos_tablas = {
        "generos.csv": "generos",
        "editoriales.csv": "editoriales",
        "tipos_cotizacion.csv": "tipos_cotizacion",
        "monedas.csv": "monedas",
        "libros.csv": "libros",
        "precios.csv": "precios",
        "stock.csv": "stock",
        "cotizaciones_dolar.csv": "cotizaciones_dolar"
    }

    # 3. Iniciamos la conexión a la base de datos
    db = ConexionDB()
    # Creamos las tablas por si no existen usando el método del Ejercicio 02
    db.crear_tablas() 
    
    # 4. Usamos nuestro context manager del Ejercicio 03
    with db.obtener_sesion() as sesion:
        for archivo_csv, tabla in archivos_tablas.items():
            ruta_csv = os.path.join(carpeta_csvs, archivo_csv)
            ruta_sql = os.path.join(carpeta_sqls, f"{tabla}.sql")
            
            # Si el archivo CSV no existe, saltamos al siguiente
            if not os.path.exists(ruta_csv):
                print(f"No se encontró el archivo {archivo_csv}, saltando...")
                continue
                
            # Abrimos el CSV para leer y el SQL para escribir
            with open(ruta_csv, mode='r', encoding='utf-8') as f_csv, \
                 open(ruta_sql, mode='w', encoding='utf-8') as f_sql:
                
                # DictReader lee la primera fila como el nombre de las columnas
                lector = csv.DictReader(f_csv)
                for fila in lector:
                    # Obtenemos los nombres de las columnas
                    columnas = ", ".join(fila.keys())
                    # Obtenemos los valores. Escapamos las comillas simples para SQL
                    valores = ", ".join(f"'{str(v).replace('\'', '\'\'')}'" for v in fila.values())
                    
                    # 5. Armamos la sentencia SQL
                    sql_insert = f"INSERT INTO {tabla} ({columnas}) VALUES ({valores});\n"
                    
                    # 6. Escribimos la sentencia en el archivo .sql
                    f_sql.write(sql_insert)
                    
                    # 7. Ejecutamos la sentencia en la base de datos
                    # Usamos text() de SQLAlchemy para ejecutar SQL puro
                    sesion.execute(text(sql_insert))
                    
        # Al salir del bloque 'with', el context manager hace el commit automáticamente
        print("Migración a SQL completada con éxito.")