# Book Manager

## Sprint 3

### Objetivo

Corregir las observaciones de la entrega del Sprint 2 y continuar con la evolución del sistema en las siguientes consignas del Sprint 3.

### Contexto

El Sprint 3 parte de la rama `Sprint_2`. El Día 1 se dedica a las correcciones del Sprint 2: relaciones bidireccionales en los modelos, repositorios que respetan la interfaz `IRepositorio`, firma original de `main`, un servicio de cotizaciones más robusto y una lista bimonetaria que permite elegir la moneda. El detalle está en el `CHANGELOG.md`.

## Sprint 2

### Objetivo

Aplicar la persistencia de datos en una base de datos relacional utilizando el ORM SQLAlchemy, consolidar la normalización de datos, y conectar el sistema a APIs externas de forma segura.

### Contexto

El sistema evoluciona para dejar atrás los archivos de texto simples y migrar toda su información a tablas relacionales robustas. Además, la aplicación ahora realiza consultas en tiempo real a la API de DolarAPI para mantener las cotizaciones sincronizadas, y permite exportar listados bimonetarios, gestionando parámetros confidenciales de forma segura mediante un archivo de entorno (`.env`).

## Ejecución

Desde el directorio `book_manager/`, asegúrate de tener el archivo `.env` configurado en la raíz, instala las dependencias y ejecuta el programa con Python 3:

```bash
# Instalar dependencias
pip install sqlalchemy

# Ejecutar el programa (en Windows usa 'py' si 'python3' no funciona)
PYTHONPATH=src python3 -m book_manager.main
```

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
PYTHONPATH=src python3 -m book_manager.main
```

La primera vez se crea la base en `datos/book_manager.sqlite3` y se cargan
los datos de los CSV. Los cambios que se hagan quedan guardados para la
próxima. Mientras se cargan datos se puede escribir `/cancelar` para volver
al menú sin guardar.

## Organización

- `src/book_manager/entities/`: entidades del dominio.
- `src/book_manager/preload_data/`: carga inicial de datos.
- `src/book_manager/repositories/`: acceso a datos.
- `src/book_manager/services/`: lógica de negocio.
- `src/book_manager/migrations/csv/`: archivos CSV para migraciones.
- `src/book_manager/ui/`: interfaz de consola.
- `src/book_manager/main.py`: punto de entrada.

## Base de datos

Los datos se gestionan mediante el ORM SQLAlchemy, apuntando a una base de datos relacional PostgreSQL alojada en Supabase. Se requiere la instalación del driver `psycopg2-binary` para establecer la comunicación. El sistema utiliza un *context manager* para manejar transacciones (commit, rollback y cierre automático de sesiones).

Para el correcto funcionamiento, el archivo `.env` en la raíz del proyecto debe contener:
- `API_URL`: Ruta a la API de cotizaciones.
- `DATABASE_URL`: Cadena de conexión a Supabase con el formato `postgresql+psycopg2://...`

Ejemplo de uso interno de la base de datos:

```python
from book_manager.database.connection import ConexionDB
from book_manager.models.models import GeneroModel
from book_manager.repositories.repositories import RepositorioGenero

# 1. Iniciar la conexión a Supabase
db = ConexionDB()
db.crear_tablas()

# 2. Instanciar el repositorio específico y realizar operaciones
repo_generos = RepositorioGenero(db)
nuevo_genero = GeneroModel(nombre="Fantasía Épica")
repo_generos.crear(nuevo_genero)
```

Algunas cosas a tener en cuenta:

- Hay que guardar primero lo que se referencia: el género y la editorial
  antes que el libro, el libro antes que su precio o su stock, etc.
- Crear un ID repetido, actualizar algo que no existe o borrar algo que
  está en uso lanza `ValueError`.
- Modificar un objeto leído no lo guarda: hay que llamar a `actualizar`.
