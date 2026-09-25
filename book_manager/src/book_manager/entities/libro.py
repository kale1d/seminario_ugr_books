from .editorial import Editorial
from .entidad_base import EntidadBase
from .genero import Genero
from .validaciones import validar_texto, validar_tipo


class Libro(EntidadBase):

    def __init__(self, id: int, isbn: str, titulo: str, autor: str,
                 editorial: Editorial, genero: Genero) -> None:
        super().__init__(id)
        self.isbn = isbn
        self.titulo = titulo
        self.autor = autor
        self.editorial = editorial
        self.genero = genero

    @property
    def isbn(self) -> str:
        return self.__isbn

    @isbn.setter
    def isbn(self, valor: str) -> None:
        # Lo guardamos como texto porque puede tener guiones o empezar con 0
        self.__isbn = validar_texto(valor, "El ISBN")

    @property
    def titulo(self) -> str:
        return self.__titulo

    @titulo.setter
    def titulo(self, valor: str) -> None:
        self.__titulo = validar_texto(valor, "El título")

    @property
    def autor(self) -> str:
        return self.__autor

    @autor.setter
    def autor(self, valor: str) -> None:
        self.__autor = validar_texto(valor, "El autor")

    @property
    def editorial(self) -> Editorial:
        return self.__editorial

    @editorial.setter
    def editorial(self, valor: Editorial) -> None:
        self.__editorial = validar_tipo(valor, Editorial, "La editorial")

    @property
    def genero(self) -> Genero:
        return self.__genero

    @genero.setter
    def genero(self, valor: Genero) -> None:
        self.__genero = validar_tipo(valor, Genero, "El género")

    def __str__(self) -> str:
        return f"{self.titulo} - {self.autor} (ISBN {self.isbn})"
