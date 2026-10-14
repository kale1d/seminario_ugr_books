import os
import json
import urllib.request
from datetime import datetime

from .servicio_base import ServicioBase
from ..entities.cotizacion_dolar import CotizacionDolar

class ServicioCotizacionDolar(ServicioBase):
    def __init__(self, repositorio, repo_tipos):
        super().__init__(repositorio)
        self.repo_tipos = repo_tipos

    def obtener_cotizaciones(self) -> None:
        """
        Descarga las cotizaciones desde la API y las registra en la base de datos.
        """
        # 1. Leemos la URL desde el archivo .env. Si no lo encuentra, usa la URL por defecto.
        url_api = os.getenv("API_URL", "https://dolarapi.com/v1/dolares")
        
        # 2. Hacemos la petición a la página web (la API)
        peticion = urllib.request.Request(url_api, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(peticion) as respuesta:
            # Transformamos el texto que llega de internet a un formato que Python entiende (diccionario)
            datos_api = json.loads(respuesta.read().decode('utf-8'))
            
        # 3. Preparamos los datos básicos para guardar
        fecha_hoy = datetime.now().date()
        tipos_en_bd = self.repo_tipos.leer_todos()
        
        # 4. Procesamos cada dólar que nos devolvió la API
        for dato in datos_api:
            nombre_api = dato.get("casa")  # Por ejemplo: "oficial", "blue"
            compra = dato.get("compra")
            venta = dato.get("venta")
            
            # Buscamos si ese tipo de dólar ya existe en nuestra base de datos
            tipo_bd = None
            for t in tipos_en_bd:
                if t.nombre.lower() == nombre_api.lower():
                    tipo_bd = t
                    break
            
            # Si encontramos el tipo y tenemos precios válidos, lo guardamos
            if tipo_bd and compra and venta:
                nueva_cotizacion = CotizacionDolar(tipo_bd, fecha_hoy, compra, venta)
                
                # Revisamos si ya guardamos la cotización de hoy para actualizarla o crearla
                existente = self.repositorio.leer_por_tipo_y_fecha(tipo_bd.id, fecha_hoy)
                if existente:
                    existente.compra = compra
                    existente.venta = venta
                    self.repositorio.actualizar(existente)
                else:
                    self.repositorio.crear(nueva_cotizacion)