CREATE TABLE IF NOT EXISTS generos (
    id INTEGER PRIMARY KEY CHECK (id > 0),
    nombre TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS editoriales (
    id INTEGER PRIMARY KEY CHECK (id > 0),
    nombre TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS monedas (
    id INTEGER PRIMARY KEY CHECK (id > 0),
    nombre TEXT NOT NULL,
    codigo TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS tipos_cotizacion (
    id INTEGER PRIMARY KEY CHECK (id > 0),
    nombre TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS libros (
    id INTEGER PRIMARY KEY CHECK (id > 0),
    isbn TEXT NOT NULL,
    titulo TEXT NOT NULL,
    autor TEXT NOT NULL,
    editorial_id INTEGER NOT NULL REFERENCES editoriales(id),
    genero_id INTEGER NOT NULL REFERENCES generos(id)
);
CREATE TABLE IF NOT EXISTS precios (
    id INTEGER PRIMARY KEY CHECK (id > 0),
    libro_id INTEGER NOT NULL REFERENCES libros(id),
    moneda_id INTEGER NOT NULL REFERENCES monedas(id),
    valor TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS stock (
    libro_id INTEGER PRIMARY KEY REFERENCES libros(id),
    cantidad INTEGER NOT NULL CHECK (cantidad >= 0)
);
CREATE TABLE IF NOT EXISTS cotizaciones_dolar (
    tipo_id INTEGER NOT NULL REFERENCES tipos_cotizacion(id),
    fecha TEXT NOT NULL,
    compra TEXT NOT NULL,
    venta TEXT NOT NULL,
    PRIMARY KEY (tipo_id, fecha)
);
