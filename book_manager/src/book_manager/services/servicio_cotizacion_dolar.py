import os
import json
import urllib.request
from datetime import datetime, date
from typing import Optional

from .servicio_base import ServicioBase
from ..entities.cotizacion_dolar import CotizacionDolar

class ServicioCotizacionDolar(ServicioBase):
    def __init__(self, repositorio, repo_tipos):
        super().__init__(repositorio)
        self.repo_tipos = repo_tipos

    def leer_ultima(self, tipo_id: int, fecha: Optional[date] = None) -> Optional[CotizacionDolar]:
        """
        Devuelve la cotización de una fecha específica, o la más reciente si no se indica fecha.
        """
        if fecha:
            # Usamos _repositorio (con guion bajo) heredado de ServicioBase
            return self._repositorio.leer_por_tipo_y_fecha(tipo_id, fecha)
        else:
            historico = self._repositorio.leer_historico_por_tipo(tipo_id)
            if not historico:
                return None
            historico_ordenado = sorted(historico, key=lambda c: c.fecha, reverse=True)
            return historico_ordenado[0]

    def obtener_cotizaciones(self) -> None:
        """
        Descarga las cotizaciones desde la API y las registra en la base de datos.
        """
        url_api = os.getenv("API_URL", "https://dolarapi.com/v1/dolares")
        
        peticion = urllib.request.Request(url_api, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(peticion) as respuesta:
            datos_api = json.loads(respuesta.read().decode('utf-8'))
            
        fecha_hoy = datetime.now().date()
        tipos_en_bd = self.repo_tipos.leer_todos()
        
        for dato in datos_api:
            nombre_api = dato.get("casa") 
            compra = dato.get("compra")
            venta = dato.get("venta")
            
            tipo_bd = None
            for t in tipos_en_bd:
                if t.nombre.lower() == nombre_api.lower():
                    tipo_bd = t
                    break
            
            if tipo_bd and compra and venta:
                nueva_cotizacion = CotizacionDolar(tipo_bd, fecha_hoy, compra, venta)
                
                existente = self._repositorio.leer_por_tipo_y_fecha(tipo_bd.id, fecha_hoy)
                if existente:
                    existente.compra = compra
                    existente.venta = venta
                    self._repositorio.actualizar(existente)
                else:
                    self._repositorio.crear(nueva_cotizacion)