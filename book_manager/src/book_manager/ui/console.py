"""Interfaz de consola del gestor de libros."""

from datetime import date
from typing import Callable, Dict, Optional, Tuple, Type, TypeVar

from ..entities.cotizacion_dolar import CotizacionDolar
from ..entities.editorial import Editorial
from ..entities.entidad_base import EntidadBase, EntidadConNombre
from ..entities.genero import Genero
from ..entities.libro import Libro
from ..entities.moneda import Moneda
from ..entities.precio import Precio
from ..entities.stock import Stock
from ..entities.tipo_cotizacion import TipoCotizacion
from ..services.servicio_base import ServicioBase
from ..services.servicio_cotizacion_dolar import ServicioCotizacionDolar
from ..services.servicio_editorial import ServicioEditorial
from ..services.servicio_genero import ServicioGenero
from ..services.servicio_libro import ServicioLibro
from ..services.servicio_moneda import ServicioMoneda
from ..services.servicio_precio import ServicioPrecio
from ..services.servicio_stock import ServicioStock
from ..services.servicio_tipo_cotizacion import ServicioTipoCotizacion

T = TypeVar("T", bound=EntidadBase)


class OperacionCancelada(Exception):
    """Se lanza cuando el usuario escribe /cancelar mientras carga datos."""


class Consola:
    """Menús de la aplicación.

    Cada opción le pide los datos al usuario y llama al servicio que
    corresponde. Las validaciones y reglas de negocio quedan en las
    entidades y los servicios; si algo falla se muestra el mensaje y se
    vuelve al menú.
    """

    def __init__(self, generos: ServicioGenero,
                 editoriales: ServicioEditorial, monedas: ServicioMoneda,
                 tipos_cotizacion: ServicioTipoCotizacion,
                 libros: ServicioLibro, precios: ServicioPrecio,
                 stock: ServicioStock,
                 cotizaciones: ServicioCotizacionDolar) -> None:
        self._generos = generos
        self._editoriales = editoriales
        self._monedas = monedas
        self._tipos_cotizacion = tipos_cotizacion
        self._libros = libros
        self._precios = precios
        self._stock = stock
        self._cotizaciones = cotizaciones

    def ejecutar(self) -> None:
        """Muestra el menú principal hasta que el usuario elige salir."""
        print("Mientras cargás datos podés escribir /cancelar para volver "
              "al menú.")
        opciones = {
            "1": ("Libros", self._menu_libros),
            "2": ("Géneros", self._menu_generos),
            "3": ("Editoriales", self._menu_editoriales),
            "4": ("Monedas", self._menu_monedas),
            "5": ("Tipos de cotización", self._menu_tipos_cotizacion),
            "6": ("Precios", self._menu_precios),
            "7": ("Stock", self._menu_stock),
            "8": ("Cotizaciones del dólar", self._menu_cotizaciones),
        }
        try:
            self._menu("GESTOR DE LIBROS", opciones, "Salir")
        except (EOFError, KeyboardInterrupt):
            print()
        print("¡Hasta luego!")

    def _menu(self, titulo: str,
              opciones: Dict[str, Tuple[str, Callable[[], None]]],
              salir: str = "Volver") -> None:
        """Muestra un menú y ejecuta la opción elegida hasta que se
        elige 0."""
        while True:
            print(f"\n=== {titulo} ===")
            for clave, (texto, _) in opciones.items():
                print(f"{clave}. {texto}")
            print(f"0. {salir}")
            opcion = input("Opción: ").strip()
            if opcion == "0":
                return
            if opcion not in opciones:
                print("Opción inválida.")
                continue
            try:
                opciones[opcion][1]()
            except OperacionCancelada:
                print("Operación cancelada.")
            except ValueError as error:
                print(f"Error: {error}")

    # ---------- Géneros, editoriales y tipos de cotización ----------

    def _menu_generos(self) -> None:
        self._menu_con_nombre("GÉNEROS", self._generos, Genero)

    def _menu_editoriales(self) -> None:
        self._menu_con_nombre("EDITORIALES", self._editoriales, Editorial)

    def _menu_tipos_cotizacion(self) -> None:
        self._menu_con_nombre("TIPOS DE COTIZACIÓN", self._tipos_cotizacion,
                              TipoCotizacion)

    def _menu_con_nombre(self, titulo: str, servicio: ServicioBase,
                         clase: Type[EntidadConNombre]) -> None:
        """Menú compartido por las entidades que solo tienen ID y nombre."""
        def listar() -> None:
            for entidad in servicio.leer_todos():
                print(f"{entidad.id} | {entidad.nombre}")

        def crear() -> None:
            id = self._pedir_id_nuevo(servicio)
            servicio.crear(clase(id, self._pedir_texto("Nombre: ")))
            print("Se creó correctamente.")

        def modificar() -> None:
            entidad = self._buscar(servicio, "ID: ")
            entidad.nombre = self._pedir_texto(
                f"Nombre [{entidad.nombre}]: ", entidad.nombre
            )
            servicio.actualizar(entidad)
            print("Se modificó correctamente.")

        self._menu(titulo, {
            "1": ("Listar", listar),
            "2": ("Crear", crear),
            "3": ("Modificar", modificar),
            "4": ("Eliminar", lambda: self._eliminar(servicio)),
        })

    # ---------- Monedas ----------

    def _menu_monedas(self) -> None:
        self._menu("MONEDAS", {
            "1": ("Listar", self._listar_monedas),
            "2": ("Crear", self._crear_moneda),
            "3": ("Modificar", self._modificar_moneda),
            "4": ("Eliminar", lambda: self._eliminar(self._monedas)),
        })

    def _listar_monedas(self) -> None:
        for moneda in self._monedas.leer_todos():
            print(f"{moneda.id} | {moneda.codigo} | {moneda.nombre}")

    def _crear_moneda(self) -> None:
        id = self._pedir_id_nuevo(self._monedas)
        nombre = self._pedir_texto("Nombre: ")
        codigo = self._pedir_texto("Código (ej: ARS): ")
        self._monedas.crear(Moneda(id, nombre, codigo))
        print("Se creó correctamente.")

    def _modificar_moneda(self) -> None:
        moneda = self._buscar(self._monedas, "ID: ")
        moneda.nombre = self._pedir_texto(f"Nombre [{moneda.nombre}]: ",
                                          moneda.nombre)
        moneda.codigo = self._pedir_texto(f"Código [{moneda.codigo}]: ",
                                          moneda.codigo)
        self._monedas.actualizar(moneda)
        print("Se modificó correctamente.")

    # ---------- Libros ----------

    def _menu_libros(self) -> None:
        self._menu("LIBROS", {
            "1": ("Listar", self._listar_libros),
            "2": ("Crear", self._crear_libro),
            "3": ("Modificar", self._modificar_libro),
            "4": ("Eliminar", lambda: self._eliminar(self._libros)),
        })

    def _listar_libros(self) -> None:
        for libro in self._libros.leer_todos():
            print(f"{libro.id} | {libro.isbn} | {libro.titulo} | "
                  f"{libro.autor} | {libro.editorial} | {libro.genero}")

    def _crear_libro(self) -> None:
        id = self._pedir_id_nuevo(self._libros)
        isbn = self._pedir_texto("ISBN: ")
        titulo = self._pedir_texto("Título: ")
        autor = self._pedir_texto("Autor: ")
        editorial = self._buscar(self._editoriales, "ID de la editorial: ")
        genero = self._buscar(self._generos, "ID del género: ")
        self._libros.crear(Libro(id, isbn, titulo, autor, editorial, genero))
        print("Se creó correctamente.")

    def _modificar_libro(self) -> None:
        libro = self._buscar(self._libros, "ID: ")
        libro.isbn = self._pedir_texto(f"ISBN [{libro.isbn}]: ", libro.isbn)
        libro.titulo = self._pedir_texto(f"Título [{libro.titulo}]: ",
                                         libro.titulo)
        libro.autor = self._pedir_texto(f"Autor [{libro.autor}]: ",
                                        libro.autor)
        libro.editorial = self._buscar(
            self._editoriales,
            f"ID de la editorial [{libro.editorial.id}]: ",
            libro.editorial,
        )
        libro.genero = self._buscar(
            self._generos, f"ID del género [{libro.genero.id}]: ",
            libro.genero,
        )
        self._libros.actualizar(libro)
        print("Se modificó correctamente.")

    # ---------- Precios ----------

    def _menu_precios(self) -> None:
        self._menu("PRECIOS", {
            "1": ("Listar", self._listar_precios),
            "2": ("Crear", self._crear_precio),
            "3": ("Modificar", self._modificar_precio),
            "4": ("Eliminar", lambda: self._eliminar(self._precios)),
            "5": ("Cotizar en pesos", self._cotizar_precio),
        })

    def _listar_precios(self) -> None:
        for precio in self._precios.leer_todos():
            print(f"{precio.id} | {precio.libro.titulo} | "
                  f"{precio.moneda.codigo} {precio.valor}")

    def _crear_precio(self) -> None:
        id = self._pedir_id_nuevo(self._precios)
        libro = self._buscar(self._libros, "ID del libro: ")
        moneda = self._buscar(self._monedas, "ID de la moneda: ")
        valor = self._pedir_importe("Valor: ")
        self._precios.crear(Precio(id, libro, moneda, valor))
        print("Se creó correctamente.")

    def _modificar_precio(self) -> None:
        precio = self._buscar(self._precios, "ID: ")
        precio.valor = self._pedir_importe(f"Valor [{precio.valor}]: ",
                                           str(precio.valor))
        self._precios.actualizar(precio)
        print("Se modificó correctamente.")

    def _cotizar_precio(self) -> None:
        precio = self._buscar(self._precios, "ID del precio: ")
        tipo = self._buscar(self._tipos_cotizacion,
                            "ID del tipo de cotización: ")
        fecha = self._pedir_fecha_opcional(
            "Fecha (AAAA-MM-DD, vacío para hoy): "
        )
        valor = self._precios.cotizar_en_pesos(precio.id, tipo.id, fecha)
        print(f"{precio.libro.titulo} sale ARS {valor:.2f} "
              f"(dólar {tipo.nombre}).")

    # ---------- Stock ----------

    def _menu_stock(self) -> None:
        self._menu("STOCK", {
            "1": ("Listar", self._listar_stock),
            "2": ("Crear", self._crear_stock),
            "3": ("Modificar cantidad", self._modificar_stock),
            "4": ("Eliminar", self._eliminar_stock),
            "5": ("Ingresar unidades", self._ingresar_stock),
            "6": ("Retirar unidades", self._retirar_stock),
        })

    def _listar_stock(self) -> None:
        for stock in self._stock.leer_todos():
            print(f"{stock.libro_id} | {stock.libro.titulo} | "
                  f"{stock.cantidad} unidades")

    def _crear_stock(self) -> None:
        libro = self._buscar(self._libros, "ID del libro: ")
        cantidad = self._pedir_entero("Cantidad: ")
        self._stock.crear(Stock(libro, cantidad))
        print("Se creó correctamente.")

    def _modificar_stock(self) -> None:
        stock = self._buscar_stock()
        stock.cantidad = self._pedir_entero(
            f"Cantidad [{stock.cantidad}]: ", stock.cantidad
        )
        self._stock.actualizar(stock)
        print("Se modificó correctamente.")

    def _eliminar_stock(self) -> None:
        stock = self._buscar_stock()
        self._stock.eliminar(stock.libro_id)
        print("Se eliminó correctamente.")

    def _ingresar_stock(self) -> None:
        stock = self._buscar_stock()
        cantidad = self._pedir_entero("Cantidad a ingresar: ")
        stock = self._stock.ingresar(stock.libro_id, cantidad)
        print(f"Ahora hay {stock.cantidad} unidades.")

    def _retirar_stock(self) -> None:
        stock = self._buscar_stock()
        cantidad = self._pedir_entero("Cantidad a retirar: ")
        stock = self._stock.retirar(stock.libro_id, cantidad)
        print(f"Ahora hay {stock.cantidad} unidades.")

    def _buscar_stock(self) -> Stock:
        libro_id = self._pedir_entero("ID del libro: ")
        stock = self._stock.leer_por_libro(libro_id)
        if stock is None:
            raise ValueError(f"El libro {libro_id} no tiene stock cargado.")
        return stock

    # ---------- Cotizaciones del dólar ----------

    def _menu_cotizaciones(self) -> None:
        self._menu("COTIZACIONES DEL DÓLAR", {
            "1": ("Listar todas", self._listar_cotizaciones),
            "2": ("Crear", self._crear_cotizacion),
            "3": ("Modificar", self._modificar_cotizacion),
            "4": ("Eliminar", self._eliminar_cotizacion),
            "5": ("Ver histórico de un tipo", self._ver_historico),
        })

    def _listar_cotizaciones(self) -> None:
        for cotizacion in self._cotizaciones.leer_todos():
            print(cotizacion)

    def _crear_cotizacion(self) -> None:
        tipo = self._buscar(self._tipos_cotizacion,
                            "ID del tipo de cotización: ")
        fecha = self._pedir_fecha("Fecha (AAAA-MM-DD): ")
        compra = self._pedir_importe("Compra: ")
        venta = self._pedir_importe("Venta: ")
        self._cotizaciones.crear(CotizacionDolar(tipo, fecha, compra, venta))
        print("Se creó correctamente.")

    def _modificar_cotizacion(self) -> None:
        cotizacion = self._buscar_cotizacion()
        cotizacion.compra = self._pedir_importe(
            f"Compra [{cotizacion.compra}]: ", str(cotizacion.compra)
        )
        cotizacion.venta = self._pedir_importe(
            f"Venta [{cotizacion.venta}]: ", str(cotizacion.venta)
        )
        self._cotizaciones.actualizar(cotizacion)
        print("Se modificó correctamente.")

    def _eliminar_cotizacion(self) -> None:
        cotizacion = self._buscar_cotizacion()
        self._cotizaciones.eliminar(cotizacion.tipo_id, cotizacion.fecha)
        print("Se eliminó correctamente.")

    def _ver_historico(self) -> None:
        tipo = self._buscar(self._tipos_cotizacion,
                            "ID del tipo de cotización: ")
        historico = self._cotizaciones.leer_historico_por_tipo(tipo.id)
        if not historico:
            print("No hay cotizaciones cargadas para ese tipo.")
        for cotizacion in historico:
            print(cotizacion)

    def _buscar_cotizacion(self) -> CotizacionDolar:
        tipo = self._buscar(self._tipos_cotizacion,
                            "ID del tipo de cotización: ")
        fecha = self._pedir_fecha("Fecha (AAAA-MM-DD): ")
        cotizacion = self._cotizaciones.leer_por_tipo_y_fecha(tipo.id, fecha)
        if cotizacion is None:
            raise ValueError("No hay cotización para ese tipo y fecha.")
        return cotizacion

    # ---------- Funciones para pedir datos ----------

    def _pedir(self, mensaje: str) -> str:
        """Lee un valor del teclado. Si se escribe /cancelar se corta la
        operación y se vuelve al menú."""
        valor = input(mensaje).strip()
        if valor.lower() == "/cancelar":
            raise OperacionCancelada()
        return valor

    def _pedir_texto(self, mensaje: str, actual: str = "") -> str:
        """Si se deja vacío devuelve el valor actual (sirve para
        modificar sin tener que reescribir todo)."""
        return self._pedir(mensaje) or actual

    def _pedir_entero(self, mensaje: str,
                      actual: Optional[int] = None) -> int:
        while True:
            valor = self._pedir(mensaje)
            if valor == "" and actual is not None:
                return actual
            try:
                return int(valor)
            except ValueError:
                print("Tiene que ser un número entero.")

    def _pedir_importe(self, mensaje: str, actual: str = "") -> str:
        """Devuelve el texto tal cual; la entidad se encarga de validarlo
        y pasarlo a Decimal. Acepta coma o punto para los decimales."""
        return self._pedir(mensaje).replace(",", ".") or actual

    def _pedir_fecha(self, mensaje: str) -> date:
        while True:
            try:
                return date.fromisoformat(self._pedir(mensaje))
            except ValueError:
                print("La fecha tiene que tener el formato AAAA-MM-DD.")

    def _pedir_fecha_opcional(self, mensaje: str) -> Optional[date]:
        """Igual que _pedir_fecha pero si se deja vacío devuelve None."""
        while True:
            valor = self._pedir(mensaje)
            if valor == "":
                return None
            try:
                return date.fromisoformat(valor)
            except ValueError:
                print("La fecha tiene que tener el formato AAAA-MM-DD.")

    def _pedir_id_nuevo(self, servicio: ServicioBase) -> int:
        """Pide un ID y avisa enseguida si ya está usado, antes de pedir
        el resto de los datos."""
        id = self._pedir_entero("ID: ")
        if servicio.leer_por_id(id) is not None:
            raise ValueError(f"Ya existe un registro con ID {id}.")
        return id

    def _buscar(self, servicio: ServicioBase[T], mensaje: str,
                actual: Optional[T] = None) -> T:
        """Pide un ID y devuelve la entidad. Si se deja vacío y hay un
        valor actual, devuelve ese."""
        valor = self._pedir(mensaje)
        if valor == "" and actual is not None:
            return actual
        if not valor.isdigit():
            raise ValueError("El ID tiene que ser un número entero.")
        entidad = servicio.leer_por_id(int(valor))
        if entidad is None:
            raise ValueError(f"No existe un registro con ID {valor}.")
        return entidad

    def _eliminar(self, servicio: ServicioBase) -> None:
        entidad = self._buscar(servicio, "ID: ")
        servicio.eliminar(entidad.id)
        print("Se eliminó correctamente.")
