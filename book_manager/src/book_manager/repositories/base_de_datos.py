"""Conexión a la base SQLite que comparten los repositorios."""

import sqlite3
from pathlib import Path
from typing import List, Union

ESQUEMA = Path(__file__).with_name("esquema.sql")


class BaseDeDatos:
    """Maneja la conexión a SQLite y crea las tablas si no existen.

    Se puede usar con `with` para que la conexión se cierre sola;
    si no, hay que llamar a cerrar() al terminar.
    """

    def __init__(
        self, ruta: Union[str, Path] = "datos/book_manager.sqlite3"
    ) -> None:
        if str(ruta) != ":memory:":
            Path(ruta).parent.mkdir(parents=True, exist_ok=True)
        self.__conexion = sqlite3.connect(ruta)
        self.__conexion.row_factory = sqlite3.Row
        # Sin esto SQLite no controla las claves foráneas
        self.__conexion.execute("PRAGMA foreign_keys = ON")
        self.__conexion.executescript(ESQUEMA.read_text(encoding="utf-8"))

    def consultar(self, sql: str, parametros: tuple = ()) -> List[sqlite3.Row]:
        """Ejecuta un SELECT y devuelve todas las filas."""
        return self.__conexion.execute(sql, parametros).fetchall()

    def ejecutar(self, sql: str, parametros: tuple = ()) -> int:
        """Ejecuta un INSERT, UPDATE o DELETE y devuelve las filas afectadas.

        Si falla se deshace el cambio. Los errores de integridad (ID
        repetido, referencia inexistente o registro en uso) se convierten
        en ValueError.
        """
        try:
            with self.__conexion:
                return self.__conexion.execute(sql, parametros).rowcount
        except sqlite3.IntegrityError as error:
            raise ValueError(
                "No se pudo completar: el registro ya existe, hace referencia "
                "a algo que no existe o está siendo usado por otro."
            ) from error

    def cerrar(self) -> None:
        """Cierra la conexión."""
        self.__conexion.close()

    def __enter__(self) -> "BaseDeDatos":
        return self

    def __exit__(self, *args: object) -> None:
        self.cerrar()
