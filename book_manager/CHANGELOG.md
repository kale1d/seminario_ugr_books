# Registro de cambios

## [Día 1 - Correcciones del Sprint 2]
- Modelos: las relaciones de `LibroModel`, `PrecioModel`, `StockModel` y `CotizacionDolarModel` ahora son bidireccionales con `back_populates`, y se agregaron las relaciones inversas en `GeneroModel`, `EditorialModel`, `MonedaModel`, `TipoCotizacionModel` y `LibroModel`.
- Repositorios: `RepositorioBase` hereda de `IRepositorio`; `RepositorioStock` y `RepositorioCotizacionDolar` implementan además sus interfaces específicas.
- Repositorios: `actualizar` verifica que el registro exista antes de hacer `merge` y lanza `ValueError` si no existe.
- Repositorios: lecturas por clave con `Session.get` y histórico de cotizaciones ordenado por fecha.
- `main`: se restituye la firma pedida `main(import_default_data: bool = True)`.
- Servicio de cotizaciones: la URL se toma solo de `API_URL` (sin URL de respaldo) y se valida que esté definida.
- Servicio de cotizaciones: la consulta a la API tiene `timeout` y manejo de errores de red y de formato (`ValueError` con mensaje claro).
- Servicio de cotizaciones: la fecha se toma de `fechaActualizacion` de la API (hoy solo si no viene informada).
- Servicio de cotizaciones: las casas que no tienen tipo cargado ya no se descartan; se da de alta el tipo y se guarda la cotización. Se mapean `bolsa` a MEP y `contadoconliqui` a CCL.
- Servicio de cotizaciones: se recuperan `crear`, `actualizar`, `eliminar`, `leer_por_tipo_y_fecha` y `leer_historico_por_tipo`, que usa la consola.
- Consola: la lista bimonetaria pide también la moneda a mostrar, además del tipo de cotización y la fecha.
- Migraciones: el armado de las sentencias SQL deja de usar una f-string con barras invertidas (solo válida desde Python 3.12).
- Estilo: imports ordenados al inicio de los módulos (sin comentarios intercalados ni imports sin usar) y docstrings en módulos, clases y métodos.

## [Sprint 2 - Fixes]
- Integración definitiva con Supabase (PostgreSQL) como base de datos en la nube.
- Instalación de `psycopg2-binary` y adaptación dinámica de la cadena de conexión en `ConexionDB` para reemplazar prefijos `postgres://` a `postgresql+psycopg2://`.
- Corrección de lazy loading (`lazy="joined"`) en los modelos para evitar errores de sesión desconectada (`DetachedInstanceError`).
- Eliminación de commits duplicados en repositorios usando `flush()`.

## [Ejercicio 08]
- Agregadas opciones en el menú interactivo para obtener cotizaciones por API, listar precios bimonetarios y exportar datos a CSV.

## [Ejercicio 07]
- Integración con la API web del dólar mediante la librería `urllib`.
- Configuración de variables de entorno mediante un archivo `.env` para proteger la URL de la API.

## [Ejercicio 06]
- Refactorización completa de la capa de repositorios para utilizar SQLAlchemy.
- Implementación de un `RepositorioBase` genérico con operaciones CRUD y repositorios específicos por entidad.

## [Ejercicio 05]
- Creación de script de migración para leer datos estructurados de archivos CSV.
- Generación automática de sentencias SQL `INSERT INTO` y ejecución en la base de datos a través de SQLAlchemy.

## [Ejercicio 04]
- Creación de modelos de base de datos (`declarative_base`) definiendo tablas, columnas y tipos de datos.
- Configuración de relaciones entre tablas usando claves foráneas (`ForeignKey` y `relationship`).

## [Ejercicio 03]
- Implementación de un context manager (`@contextmanager`) para encapsular las operaciones de base de datos con `commit`, `rollback` y `close`.

## [Ejercicio 02]
- Configuración inicial del motor de base de datos creando la clase `ConexionDB` con SQLAlchemy.

## [Ejercicio 01]
- Inicialización de la rama `Sprint_2` y reestructuración del entorno de trabajo.

---

# Registro de cambios Sprint 1

## [Ejercicio 7] | día 07

- main.py arma la base, los repositorios y los servicios y abre la consola.
- Parámetro import_default_data para cargar o no los datos de los CSV.
- La base se guarda en book_manager/datos (ignorada en git).

## [Ejercicio 6] | día 06

- Consola con un menú principal y un submenú por entidad para listar,
  crear, modificar y eliminar.
- Opciones extra para ingresar y retirar stock, ver el histórico del dólar
  y cotizar un precio en pesos.
- Si hay un error se muestra el mensaje y se vuelve al menú; con /cancelar
  se puede salir de una carga a mitad de camino.

## [Ejercicio 5] | día 05

- Archivos CSV en migrations/csv con los datos iniciales de las ocho
  entidades (al menos 10 registros cada una).
- preload_data.py lee los CSV y los carga en la base a través de los
  servicios, en orden para respetar las relaciones.
- Si un registro ya existe se saltea, así la carga se puede repetir.

## [Ejercicio 4] | día 04

- Un servicio por entidad con la lógica de negocio, que usa los
  repositorios a través de sus interfaces.
- ServicioBase con el CRUD común y validaciones antes de guardar.
- Reglas: ISBN y código de moneda únicos, un precio por libro y moneda,
  referencias existentes y una cotización por tipo y fecha.
- Ingreso y retiro de unidades de stock sin permitir quedar en negativo.
- Conversión de precios en USD a ARS con la última cotización vigente.

## [Ejercicio 3] | día 03

- Se agregaron las interfaces IRepositorio, IRepositorioStock e
  IRepositorioCotizacionDolar tomando como base las de la consigna.
- Un repositorio por entidad con su CRUD, guardando en una base SQLite.
- RepositorioBase con el CRUD genérico por ID para no repetir el SQL.
- Stock se busca por libro y las cotizaciones por tipo y fecha.

## [Ejercicio 2] | día 02

- Se crearon las entidades Libro, Genero, Editorial, Moneda, TipoCotizacion,
  Precio, Stock y CotizacionDolar, cada una en su archivo.
- Atributos privados con properties y validaciones en los setters.
- Clase base EntidadBase (ID) y EntidadConNombre para no repetir código.
- Los importes se manejan con Decimal.

## [Ejercicio 1] | día 01

- Estructura inicial del proyecto para Sprint_1.
