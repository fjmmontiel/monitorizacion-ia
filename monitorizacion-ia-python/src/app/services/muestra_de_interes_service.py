"""
Servicio de registro de muestras de interés hipotecarias.

Proporciona funcionalidad para registrar muestras de interés de clientes
en productos hipotecarios mediante autenticación OAuth2 y API REST.
"""

import requests
from app.unicaja_services_config import UnicajaServicesConfig
from qgdiag_lib_arquitectura import CustomLogger


logger = CustomLogger("Servicio para guardar muestra de interes")


class MuestraDeInteresService:
    """
    Servicio para registro de muestras de interés en productos hipotecarios.

    Gestiona el alta de muestras de interés de clientes con autenticación
    OAuth2 y manejo de errores específicos del sistema bancario.
    """

    def __init__(self):
        config = UnicajaServicesConfig()

        # Configuración de la API y OAuth
        self.client_id = config.client_id
        self.client_secret = config.client_secret
        self.token_url = config.url_token_oauth2
        self.api_url = config.api_muestra_interes_url

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

    def _post_alta_muestra_interes(self, token, input_data):
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        # Se elimina este campo porque la api no lo admite
        input_data["tl"]["datosPreEval"].pop("precioVivienda", None)
        response = requests.post(self.api_url, headers=headers, json=input_data)
        error_output = ""

        # Detectar cualquier código != 200 y loguear (estandarizado)
        if not (200 <= response.status_code <= 299):
            logger.error("Problema de conexión a la API: " + self.api_url)
            try:
                body_resp = response.json()
            except ValueError:
                body_resp = response.text
            logger.info(
                f"Tipo de error=HTTP {response.status_code}, response={body_resp}, codigo={response.status_code}"
            )

            # Mantener la lógica existente de mensajes específicos
            try:
                response.raise_for_status()
            except requests.exceptions.HTTPError as http_err:
                if "412 Client Error" in f"{http_err}":
                    error_output = (
                        f"HTTP error occurred: {http_err} - "
                        "No se puede guardar la muestra de interés. "
                        "El cliente podría tener un expediente abierto en otra oficina."
                    )
                else:
                    try:
                        error_detail = response.json()
                    except ValueError:
                        error_detail = f"Response content: {response.text}"
                    error_output = f"HTTP error occurred: {http_err} - {error_detail}"
            return {
                "error": error_output
                or f"HTTP error occurred: {response.status_code} - {body_resp}"
            }

        if error_output != "":
            return {"error": error_output}
        return response.json()

    def call(self, api_request: str):
        response = ""
        try:
            logger.info("Llamada a servicio para guardar una muestra de interés")
            token = self._get_oauth_token(self.client_id, self.client_secret)
            response = self._post_alta_muestra_interes(token, api_request)
        except Exception as e:
            logger.info(f"Error al guardar la muestra de interés: {e}")
        return response
