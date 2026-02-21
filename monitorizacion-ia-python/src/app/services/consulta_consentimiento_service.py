"""
Servicio de consulta de consentimientos de clientes.

Gestiona la consulta del estado de consentimientos de clientes mediante
autenticación JWT y API REST, procesando diferentes estados de consentimiento.
"""

import requests
from app.unicaja_services_config import UnicajaServicesConfig
from app.models.models_APIRequest import ConsentimientoRequest
from qgdiag_lib_arquitectura import CustomLogger


logger = CustomLogger("Servicio para la consulta de consentimiento.")


class ConsultaConsentimientoService:
    """
    Servicio para consultar el estado de consentimientos de clientes.

    Maneja autenticación JWT y diferentes estados de consentimiento
    (Cliente, Precliente, Nueva alta).
    """

    def __init__(self, headers):
        config = UnicajaServicesConfig()

        # URLs
        self.api_url = config.api_consulta_consentimiento
        self.headers = headers

    def _consulta_consentimiento(self, body: ConsentimientoRequest):
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

    def call(self, data: ConsentimientoRequest):
        try:
            logger.info("Llamada a servicio para consulta de consentimiento")
            body = data.model_dump()
            response = self._consulta_consentimiento(body)
            situacion = response.get("indicadorSituacion")
            if situacion == "C":
                return "Cliente: consentimiento ya aceptado."
            if situacion == "P":
                return "Precliente: consentimiento ya aceptado."
            if situacion == "A":
                return "Nueva alta: mail enviado para aceptar consentimiento."
            return response
        except Exception as e:
            return {"error": str(e)}
