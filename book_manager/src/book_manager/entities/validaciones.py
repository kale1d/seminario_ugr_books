"""Validaciones que se repiten en varias entidades."""

from decimal import Decimal, InvalidOperation
from typing import Union


def validar_texto(valor: str, campo: str) -> str:
    """Devuelve el texto sin espacios en los extremos.

    Lanza un error si no es un texto o si está vacío.
    """
    if not isinstance(valor, str):
        raise TypeError(f"{campo} debe ser un texto.")
    if valor.strip() == "":
        raise ValueError(f"{campo} no puede estar vacío.")
    return valor.strip()


def validar_tipo(valor: object, clase: type, campo: str) -> None:
    """Lanza TypeError si el valor no es una instancia de la clase."""
    if not isinstance(valor, clase):
        raise TypeError(f"{campo} debe ser de tipo {clase.__name__}.")


def validar_importe(valor: Union[Decimal, int, float, str]) -> Decimal:
    """Convierte el valor a Decimal y controla que no sea negativo.

    Se usa Decimal para no arrastrar errores de redondeo con la plata.
    Se pasa por str() para que un float como 0.1 quede exacto.
    """
    try:
        importe = Decimal(str(valor))
    except InvalidOperation:
        raise ValueError(f"'{valor}' no es un importe válido.")
    if importe < 0:
        raise ValueError("El importe no puede ser negativo.")
    return importe
