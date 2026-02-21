"""
Servicio de consulta de datos de clientes.

Proporciona funcionalidad para consultar información de clientes
en los sistemas de Unicaja mediante autenticación OAuth2 y API REST.
"""

import requests
from app.unicaja_services_config import UnicajaServicesConfig
from qgdiag_lib_arquitectura import CustomLogger


logger = CustomLogger("Servicio para la consulta de un cliente.")


class ConsultaClienteService:
    """
    Servicio para consultar datos de clientes en los sistemas de Unicaja.

    Gestiona la autenticación OAuth2 y las consultas a la API de clientes.
    """

    def __init__(self):
        config = UnicajaServicesConfig()

        # Configuración de la API y OAuth. DESARROLLO
        self.client_id = config.client_id
        self.client_secret = config.client_secret
        self.url_token_oauth2 = config.url_token_oauth2
        self.api_url = config.api_consulta_cliente_url

    def _get_oauth_token(self, client_id, client_secret):
        url = self.url_token_oauth2
        payload = {
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret,
            "scope": "api-interno",
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        response = requests.post(url, data=payload, headers=headers)
        response.raise_for_status()
        return response.json()["access_token"]

    def _consulta_datos_cliente(self, token, nif):
        url = self.api_url
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        input_data = {"codIden": nif}

        response = requests.post(url, json=input_data, headers=headers)

        if not (200 <= response.status_code <= 299):
            logger.error("Problema de conexión a la API: " + self.api_url)
            try:
                body = response.json()
            except ValueError:
                body = response.text
            logger.info(
                f"Tipo de error=HTTP {response.status_code}, response={body}, codigo={response.status_code}"
            )
            return {"error": f"HTTP error occurred: {response.status_code} - {body}"}

        # OK (200)
        try:
            return response.json()
        except ValueError:
            return {"error": f"Respuesta no JSON: {response.text}"}

    def call(self, nif: str):
        response = ""
        try:
            logger.info("Llama a servicio para consulta de cliente")
            token = self._get_oauth_token(self.client_id, self.client_secret)
            response = self._consulta_datos_cliente(token, nif)
        except Exception as e:
            return f"Error: {e}"
        return response
