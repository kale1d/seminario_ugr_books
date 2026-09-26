# Registro de cambios

## [Ejercicio 7]

- main.py arma la base, los repositorios y los servicios y abre la consola.
- Parámetro import_default_data para cargar o no los datos de los CSV.
- La base se guarda en book_manager/datos (ignorada en git).

## [Ejercicio 6]

- Consola con un menú principal y un submenú por entidad para listar,
  crear, modificar y eliminar.
- Opciones extra para ingresar y retirar stock, ver el histórico del dólar
  y cotizar un precio en pesos.
- Si hay un error se muestra el mensaje y se vuelve al menú; con /cancelar
  se puede salir de una carga a mitad de camino.

## [Ejercicio 5]

- Archivos CSV en migrations/csv con los datos iniciales de las ocho
  entidades (al menos 10 registros cada una).
- preload_data.py lee los CSV y los carga en la base a través de los
  servicios, en orden para respetar las relaciones.
- Si un registro ya existe se saltea, así la carga se puede repetir.

## [Ejercicio 4]

- Un servicio por entidad con la lógica de negocio, que usa los
  repositorios a través de sus interfaces.
- ServicioBase con el CRUD común y validaciones antes de guardar.
- Reglas: ISBN y código de moneda únicos, un precio por libro y moneda,
  referencias existentes y una cotización por tipo y fecha.
- Ingreso y retiro de unidades de stock sin permitir quedar en negativo.
- Conversión de precios en USD a ARS con la última cotización vigente.

## [Ejercicio 3]

- Se agregaron las interfaces IRepositorio, IRepositorioStock e
  IRepositorioCotizacionDolar tomando como base las de la consigna.
- Un repositorio por entidad con su CRUD, guardando en una base SQLite.
- RepositorioBase con el CRUD genérico por ID para no repetir el SQL.
- Stock se busca por libro y las cotizaciones por tipo y fecha.

## [Ejercicio 2]

- Se crearon las entidades Libro, Genero, Editorial, Moneda, TipoCotizacion,
  Precio, Stock y CotizacionDolar, cada una en su archivo.
- Atributos privados con properties y validaciones en los setters.
- Clase base EntidadBase (ID) y EntidadConNombre para no repetir código.
- Los importes se manejan con Decimal.

## [Ejercicio 1]

- Estructura inicial del proyecto para Sprint_1.
