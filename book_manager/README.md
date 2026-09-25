# Book Manager

## Sprint 1

### Objetivo

Desarrollar una aplicación de consola (CLI) en Python que permita gestionar
el inventario de una librería, cotizar los libros en tiempo real según el
valor del dólar y comparar precios automáticamente con la competencia web.

### Contexto

Una librería con venta al público necesita modernizar su sistema de gestión
de inventario. Como los costos de importación de libros cambian todo el
tiempo, el sistema tiene que manejar precios en distintas monedas y seguir
de cerca la cotización del dólar para mantener los valores actualizados.

## Ejecución

Desde el directorio `book_manager/`, con Python 3:

```bash
python3 src/book_manager/main.py
```

## Organización

- `src/book_manager/entities/`: entidades del dominio.
- `src/book_manager/preload_data/`: carga inicial de datos.
- `src/book_manager/repositories/`: acceso a datos.
- `src/book_manager/services/`: lógica de negocio.
- `src/book_manager/migrations/csv/`: archivos CSV para migraciones.
- `src/book_manager/ui/`: interfaz de consola.
- `src/book_manager/main.py`: punto de entrada.

## Base de datos

Los datos se guardan en SQLite, que ya viene con Python. Por defecto el
archivo se crea en `datos/book_manager.sqlite3`. Ejemplo de uso (con
`PYTHONPATH=src` desde `book_manager/`):

```python
from book_manager.entities import Genero
from book_manager.repositories import BaseDeDatos, RepositorioGenero

with BaseDeDatos() as base:
    generos = RepositorioGenero(base)
    generos.crear(Genero(1, "Novela"))
    print(generos.leer_todos())
```

Algunas cosas a tener en cuenta:

- Hay que guardar primero lo que se referencia: el género y la editorial
  antes que el libro, el libro antes que su precio o su stock, etc.
- Crear un ID repetido, actualizar algo que no existe o borrar algo que
  está en uso lanza `ValueError`.
- Modificar un objeto leído no lo guarda: hay que llamar a `actualizar`.
