"""
Servicio de registro de log operacional.
"""

import requests
from app.unicaja_services_config import UnicajaServicesConfig
from app.models.models_APIRequest import LogOperacionalRequest

from qgdiag_lib_arquitectura import CustomLogger


logger = CustomLogger("Servicio de log operacional")


class LogOperacionalService:
    """
    Servicio para registro de log operacional.
    """

    def __init__(self, headers):
        config = UnicajaServicesConfig()

        # URLs
        self.api_url = config.api_log_operacional
        self.headers = headers

    def _registrar_log(self, body: LogOperacionalRequest):
        """Envía el log operacional a la API y mantiene el mismo estilo de logs."""
        logger.info("Llamada a servicio para registrar log operacional")

        headers = {
            "Channel": "interno",
            "Connection": "keep-alive",
            "Content-Type": "application/json",
            "Token": self.headers["Token"],
            "Accept": "*/*",
        }

        response = requests.post(self.api_url, headers=headers, json=body.model_dump())

        # Detectar cualquier código != 2xx y loguear igual que en _consulta_bonificaciones
        if response.status_code < 200 or response.status_code >= 300:
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

        # OK (2xx)
        try:
            return response.json()
        except ValueError:
            return {"error": f"Respuesta no JSON: {response.text}"}

    def call(self, data: LogOperacionalRequest):
        """Ejecuta todo el flujo"""
        try:
            logger.info(
                f"[DEBUG] Iniciando flujo de log operacional para {data.modulo} - {data.operacion}"
            )
            result = self._registrar_log(data)

            if result.get("status") == "Success":
                return f"Log registrado correctamente: {result.get('message')}"
            return f"Respuesta inesperada: {result}"
        except Exception as e:
            logger.info(f"[ERROR] Fallo en el flujo de registro de log: {e}")
            return {"error": str(e)}
