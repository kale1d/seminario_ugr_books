"""Validaciones que se repiten en varias entidades."""

from decimal import Decimal, InvalidOperation


def validar_texto(valor: str, campo: str) -> str:
    if not isinstance(valor, str):
        raise TypeError(f"{campo} debe ser un texto.")
    if valor.strip() == "":
        raise ValueError(f"{campo} no puede estar vacío.")
    return valor.strip()


def validar_tipo(valor, clase, campo: str):
    if not isinstance(valor, clase):
        raise TypeError(f"{campo} debe ser de tipo {clase.__name__}.")
    return valor


def validar_importe(valor) -> Decimal:
    # Usamos Decimal para no arrastrar errores de redondeo con la plata.
    # Se pasa por str() para que un float como 0.1 no quede como 0.1000000000000000055...
    try:
        importe = Decimal(str(valor))
    except InvalidOperation:
        raise ValueError(f"'{valor}' no es un importe válido.")
    if importe < 0:
        raise ValueError("El importe no puede ser negativo.")
    return importe
