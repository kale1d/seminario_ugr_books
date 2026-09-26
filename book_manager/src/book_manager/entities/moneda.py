from .entidad_base import EntidadConNombre
from .validaciones import validar_texto


class Moneda(EntidadConNombre):
    """Además del nombre guarda el código ISO (ARS, USD...)."""

    def __init__(self, id: int, nombre: str, codigo: str) -> None:
        super().__init__(id, nombre)
        self.codigo = codigo

    @property
    def codigo(self) -> str:
        return self.__codigo

    @codigo.setter
    def codigo(self, valor: str) -> None:
        codigo = validar_texto(valor, "El código").upper()
        if len(codigo) != 3 or not codigo.isalpha():
            raise ValueError("El código debe tener 3 letras (ej: ARS).")
        self.__codigo = codigo
