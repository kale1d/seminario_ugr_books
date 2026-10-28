"""Comparación de los precios propios con los de la web y generación del
archivo CSV de alertas."""

import csv
import re
import unicodedata
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from difflib import SequenceMatcher
from pathlib import Path
from typing import Dict, List, Optional

from ..entities.libro import Libro
from ..entities.precio import Precio
from ..entities.precio_web import PrecioWeb
from ..entities.tipo_cotizacion import TipoCotizacion
from ..repositories.interfaces import IRepositorio, IRepositorioPrecioWeb
from .servicio_precio import ServicioPrecio

# Carpeta donde se guardan los CSV y reportes generados.
CARPETA_REPORTES = Path(__file__).resolve().parents[1] / "reportes"

# Parecido mínimo (de 0 a 1) para considerar que dos títulos son el mismo.
SIMILITUD_MINIMA = 0.9


def normalizar_titulo(titulo: str) -> str:
    """Deja el título en minúsculas, sin tildes ni signos, para poder
    compararlo ("El túnel" y "EL TUNEL" quedan iguales)."""
    descompuesto = unicodedata.normalize("NFD", titulo)
    sin_tildes = "".join(
        c for c in descompuesto if unicodedata.category(c) != "Mn"
    )
    return re.sub(r"[^a-z0-9]+", " ", sin_tildes.lower()).strip()


def sin_parentesis(texto: str) -> str:
    """Quita lo que va entre paréntesis ("El principito ( tapa dura )"
    queda como "El principito")."""
    return re.sub(r"\([^)]*\)", " ", texto)


@dataclass(frozen=True)
class Comparacion:
    """Resultado de comparar un libro del catálogo con la web.

    Si el libro no tiene precio propio o no se encontró en la web, los
    campos de la comparación quedan en None.

    Attributes:
        libro_id: ID del libro del catálogo.
        libro: Título del libro del catálogo.
        precio_interno: Precio propio en pesos.
        precio_web: Precio web en pesos (el más barato encontrado).
        titulo_web: Título de la ficha elegida en la web.
        url_detalle: URL de la ficha elegida.
        fecha_extraccion: Fecha y hora de la extracción del precio web.
        diferencia: Precio interno menos precio web.
        diferencia_porcentaje: Diferencia como porcentaje del precio
            interno (positiva si la web es más barata).
    """

    libro_id: int
    libro: str
    precio_interno: Optional[Decimal] = None
    precio_web: Optional[Decimal] = None
    titulo_web: Optional[str] = None
    url_detalle: Optional[str] = None
    fecha_extraccion: Optional[datetime] = None
    diferencia: Optional[Decimal] = None
    diferencia_porcentaje: Optional[Decimal] = None

    @property
    def tiene_coincidencia(self) -> bool:
        """True si se pudo comparar el libro con la web."""
        return self.diferencia is not None


@dataclass(frozen=True)
class ResultadoAlertas:
    """Resumen de una generación de alertas.

    Attributes:
        ruta: Archivo CSV generado.
        total_libros: Libros del catálogo analizados.
        total_comparados: Libros que se pudieron comparar con la web.
        total_alertas: Libros cuya diferencia superó el umbral.
    """

    ruta: Path
    total_libros: int
    total_comparados: int
    total_alertas: int


class ServicioComparacion:
    """Compara el precio propio de cada libro con el más barato que se
    encontró en la web y genera el CSV de alertas."""

    def __init__(self, libros: IRepositorio[Libro],
                 precios: ServicioPrecio,
                 precios_web: IRepositorioPrecioWeb,
                 tipos: IRepositorio[TipoCotizacion],
                 carpeta_reportes: Path = CARPETA_REPORTES,
                 tipo_cotizacion: str = "Oficial") -> None:
        """Guarda los repositorios y servicios que usa la comparación.

        Args:
            libros (IRepositorio[Libro]): Repositorio de libros.
            precios (ServicioPrecio): Servicio de precios propios.
            precios_web (IRepositorioPrecioWeb): Precios obtenidos de la
                web.
            tipos (IRepositorio[TipoCotizacion]): Tipos de cotización.
            carpeta_reportes (Path): Carpeta donde se guardan los CSV.
            tipo_cotizacion (str): Tipo de dólar con el que se convierten
                los precios propios que están en USD.
        """
        self._libros = libros
        self._precios = precios
        self._precios_web = precios_web
        self._tipos = tipos
        self._carpeta = Path(carpeta_reportes)
        self._tipo_cotizacion = tipo_cotizacion

    def comparar(self) -> List[Comparacion]:
        """Compara cada libro del catálogo con la web.

        Returns:
            List[Comparacion]: Una comparación por libro del catálogo.
        """
        tipo_id = self._id_tipo_cotizacion()
        web_por_libro: Dict[int, List[PrecioWeb]] = {}
        for web in self._precios_web.leer_ultimas():
            web_por_libro.setdefault(web.libro_id, []).append(web)
        precios_por_libro: Dict[int, List[Precio]] = {}
        for precio in self._precios.leer_todos():
            precios_por_libro.setdefault(precio.libro.id, []).append(precio)

        comparaciones = []
        for libro in self._libros.leer_todos():
            interno = self._precio_interno(
                precios_por_libro.get(libro.id, []), tipo_id
            )
            web = self._mejor_coincidencia(
                libro, web_por_libro.get(libro.id, [])
            )
            comparaciones.append(self._armar(libro, interno, web))
        return comparaciones

    def generar_alertas(self, umbral: Decimal) -> ResultadoAlertas:
        """Genera un CSV con los libros cuya diferencia de precio, en
        porcentaje y en cualquier sentido, es igual o mayor al umbral.

        Args:
            umbral (Decimal): Diferencia porcentual mínima (por ejemplo,
                10 para 10%).

        Returns:
            ResultadoAlertas: Archivo generado y totales.

        Raises:
            ValueError: Si el umbral es negativo.
        """
        if umbral < 0:
            raise ValueError("La diferencia mínima no puede ser negativa.")
        comparaciones = self.comparar()
        alertas = [
            c for c in comparaciones
            if c.tiene_coincidencia and abs(c.diferencia_porcentaje) >= umbral
        ]

        self._carpeta.mkdir(parents=True, exist_ok=True)
        ruta = self._carpeta / f"alertas_{datetime.now():%Y%m%d_%H%M%S}.csv"
        # utf-8-sig para que Excel muestre bien las tildes
        with open(ruta, mode="w", newline="", encoding="utf-8-sig") as f:
            escritor = csv.writer(f)
            escritor.writerow([
                "Libro", "Precio interno", "Precio web", "Diferencia",
                "Diferencia %", "Estado", "Título web", "URL",
                "Fecha de extracción",
            ])
            for c in alertas:
                estado = ("Web más barata" if c.diferencia > 0
                          else "Web más cara")
                escritor.writerow([
                    c.libro, c.precio_interno, c.precio_web, c.diferencia,
                    c.diferencia_porcentaje, estado, c.titulo_web,
                    c.url_detalle, f"{c.fecha_extraccion:%Y-%m-%d %H:%M}",
                ])

        return ResultadoAlertas(
            ruta=ruta,
            total_libros=len(comparaciones),
            total_comparados=sum(c.tiene_coincidencia for c in comparaciones),
            total_alertas=len(alertas),
        )

    def _id_tipo_cotizacion(self) -> int:
        """Devuelve el ID del tipo de cotización usado para convertir.

        Raises:
            ValueError: Si el tipo no está cargado.
        """
        for tipo in self._tipos.leer_todos():
            if tipo.nombre.lower() == self._tipo_cotizacion.lower():
                return tipo.id
        raise ValueError(
            f"No existe el tipo de cotización {self._tipo_cotizacion!r}."
        )

    def _precio_interno(self, precios: List[Precio],
                        tipo_id: int) -> Optional[Decimal]:
        """Precio propio en pesos: el que está en ARS o, si no hay, el que
        está en USD convertido con la última cotización."""
        for precio in precios:
            if precio.moneda.codigo == "ARS":
                return precio.valor
        for precio in precios:
            try:
                return self._precios.cotizar_en_pesos(precio.id, tipo_id)
            except ValueError:
                continue
        return None

    @staticmethod
    def _mejor_coincidencia(libro: Libro,
                            candidatos: List[PrecioWeb]) -> Optional[PrecioWeb]:
        """Entre los resultados web con título parecido al del libro,
        devuelve el de menor precio."""
        titulo = normalizar_titulo(libro.titulo)
        parecidos = [
            c for c in candidatos
            if SequenceMatcher(
                None, titulo,
                normalizar_titulo(sin_parentesis(c.titulo_web))
            ).ratio() >= SIMILITUD_MINIMA
        ]
        return min(parecidos, key=lambda c: c.precio) if parecidos else None

    @staticmethod
    def _armar(libro: Libro, interno: Optional[Decimal],
               web: Optional[PrecioWeb]) -> Comparacion:
        """Arma la comparación de un libro."""
        if interno is None or web is None or interno == 0:
            return Comparacion(libro.id, libro.titulo, precio_interno=interno)
        diferencia = interno - web.precio
        return Comparacion(
            libro_id=libro.id, libro=libro.titulo, precio_interno=interno,
            precio_web=web.precio, titulo_web=web.titulo_web,
            url_detalle=web.url_detalle,
            fecha_extraccion=web.fecha_extraccion, diferencia=diferencia,
            diferencia_porcentaje=(diferencia / interno * 100).quantize(
                Decimal("0.01")
            ),
        )