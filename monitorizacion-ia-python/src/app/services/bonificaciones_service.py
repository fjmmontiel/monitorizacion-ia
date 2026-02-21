"""
Servicio de consulta de bonificaciones de productos hipotecarios.
"""

import requests
from app.unicaja_services_config import UnicajaServicesConfig
from qgdiag_lib_arquitectura import CustomLogger


logger = CustomLogger(
    "Servicio para la consulta de bonificaciones de productos hipotecarios."
)


class BonificacionesService:
    """
    Servicio para consultar bonificaciones de productos hipotecarios.
    """

    def __init__(self, headers):
        config = UnicajaServicesConfig()

        # URLs
        self.api_url = config.api_bonificaciones
        self.headers = headers

    def _consulta_bonificaciones(self, body: dict):
        response = requests.post(self.api_url, headers=self.headers, json=body)

        # Detectar cualquier código != 200 y loguear
        if not (200 <= response.status_code <= 299):
            logger.error("Problema de conexión a la API: " + self.api_url)
            try:
                body_resp = response.json()
            except ValueError:
                body_resp = response.text
            logger.info(
                f"Tipo de error=HTTP {response.status_code}, response={body_resp}, codigo={response.status_code}"
            )
            return {
                "error": f"HTTP error occurred: {response.status_code} - {body_resp}"
            }

        # OK (200)
        try:
            return response.json()
        except ValueError:
            return {"error": f"Respuesta no JSON: {response.text}"}

    def call(self, data: dict):
        try:
            logger.info("Llamada a servicio para consulta de bonificaciones")

            response = self._consulta_bonificaciones(body=data)

            return response
        except Exception as e:
            return {"error": str(e)}
