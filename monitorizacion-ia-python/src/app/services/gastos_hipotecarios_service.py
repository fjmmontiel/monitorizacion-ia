"""
Servicio de consulta de gastos hipotecarios.

Proporciona funcionalidad para consultar los gastos asociados a hipotecas
mediante el servicio web público de Unicaja Banco. No incluye gastos de tasación.
"""

import requests
from app.unicaja_services_config import UnicajaServicesConfig
from qgdiag_lib_arquitectura import CustomLogger


logger = CustomLogger("Simulador para cálculo de gastos hipotecarios.")

# Los gastos de tasación no están contenidos en esta llamada, para obtener el coste de tasación hay que
# invocar la simulacion (SimulacionService)
PROVINCIA_MAP = {
    "01": "pv",
    "02": "cm",
    "03": "va",
    "04": "an",
    "05": "cl",
    "06": "ex",
    "07": "ba",
    "08": "ct",
    "09": "cl",
    "10": "ex",
    "11": "an",
    "12": "va",
    "13": "cm",
    "14": "an",
    "15": "ga",
    "16": "cm",
    "17": "ct",
    "18": "an",
    "19": "cm",
    "20": "pv",
    "21": "an",
    "22": "ar",
    "23": "an",
    "24": "cl",
    "25": "ct",
    "26": "lr",
    "27": "ga",
    "28": "ma",
    "29": "an",
    "30": "mu",
    "31": "na",
    "32": "ga",
    "33": "as",
    "34": "cl",
    "35": "ca",
    "36": "ga",
    "37": "cl",
    "38": "ca",
    "39": "cn",
    "40": "cl",
    "41": "an",
    "42": "cl",
    "43": "ct",
    "44": "ar",
    "45": "cm",
    "46": "va",
    "47": "cl",
    "48": "pv",
    "49": "cl",
    "50": "ar",
    "51": "ce",
    "52": "me",
}

TIPO_VIVIENDA_MAP = {1: "cvt", 2: "hip"}


class GastosHipotecariosService:
    """
    Servicio para consultar gastos hipotecarios por provincia e importe.

    Consulta los gastos que asume el cliente en operaciones hipotecarias,
    excluyendo los gastos de tasación que requieren simulación separada.
    """

    def __init__(self):
        config = UnicajaServicesConfig()

        # Configuración de la API y OAuth
        self.client_id = config.client_id
        self.client_secret = config.client_secret
        self.token_url = config.url_token_oauth2
        self.api_url = config.api_gastos_hipotecarios

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

    def _call_prestamo_service(self, token, data):
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        response = requests.post(self.api_url, headers=headers, json=data)

        # Detectar cualquier código != 200 y loguear
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

    def call(self, importe: int, tipo_vivienda: int, id_provincia: str):
        response = ""

        try:
            logger.info("Llamada a servicio para consulta de gastos hipotecarios")
            zona = PROVINCIA_MAP.get(id_provincia)
            tipo = TIPO_VIVIENDA_MAP.get(tipo_vivienda)
            data = {"importe": importe, "tipo": tipo, "zonaGeo": zona}

            token = self._get_oauth_token(self.client_id, self.client_secret)
            response = self._call_prestamo_service(token, data)
        except Exception as e:
            response = f"Error: {e}"
        return response
