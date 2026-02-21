"""
Servicio de cancelacion de muestras de interés.

Proporciona funcionalidad para cancelar muestras de interés de clientes
en productos hipotecarios mediante autenticación OAuth2 y API REST.
"""

import requests
from app.unicaja_services_config import UnicajaServicesConfig
from qgdiag_lib_arquitectura import CustomLogger


logger = CustomLogger("Servicio para cencelar una muestra de interes")


class CancelacionMuestraDeInteresService:
    """
    Servicio para cancelación de muestras de interés en productos hipotecarios.

    Gestiona la cancelación de muestras de interés de clientes con autenticación
    OAuth2 y manejo de errores específicos del sistema bancario.
    """

    def __init__(self):
        config = UnicajaServicesConfig()

        # Configuración de la API y OAuth
        self.client_id = config.client_id
        self.client_secret = config.client_secret
        self.token_url = config.url_token_oauth2
        self.api_url = config.api_cancelar_muestra_interes_url

    def _get_oauth_token(self, client_id, client_secret):
        data = {
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret,
            "scope": "api-interno",
        }
        response = requests.post(self.token_url, data=data)
        response.raise_for_status()
        return response.json()["access_token"]

    def _post_cancelar_muestra_interes(self, token, input_data):
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        response = requests.post(self.api_url, headers=headers, json=input_data)

        # Detectar cualquier código != 200 y loguear
        if not (200 <= response.status_code <= 299):
            # Mensaje estándar
            logger.error("Problema de conexión a la API: " + self.api_url)

            # Cuerpo para el log informativo
            try:
                body = response.json()
            except ValueError:
                body = response.text

            # Detalle informativo
            logger.info(
                f"Tipo de error=HTTP {response.status_code}, response={body}, codigo={response.status_code}"
            )

            # Mantener salida similar a la original (dict con 'error')
            # Respetando tu mensaje específico para 412
            if response.status_code == 412:
                return {
                    "error": "HTTP error occurred: 412 - No se puede cancelar la muestra de interés."
                }
            else:
                return {
                    "error": f"HTTP error occurred: {response.status_code} - {body}"
                }

        # Caso OK (200): igual que antes
        try:
            return response.json()
        except ValueError:
            return {"error": f"Respuesta no JSON: {response.text}"}

    def call(self, num_expediente: str):
        response = ""
        try:
            logger.info("Llamada a servicio para cancelar muestra de interés")
            input_data = {
                "motivo": "11",
                "numeroExpediente": num_expediente,
                "accionSG": "CEST",
                "estadoFinancia": "09",
            }

            token = self._get_oauth_token(self.client_id, self.client_secret)
            response = self._post_cancelar_muestra_interes(token, input_data)
        except Exception as e:
            response = f"Error: {e}"
        return response
