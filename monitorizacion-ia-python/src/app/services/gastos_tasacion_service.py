"""
Modulo para calcular los gastos de tasacion
Servicio de cálculo de gastos de tasación.

Proporciona funcionalidad para calcular los gastos de tasación de inmuebles
mediante el simulador hipotecario web de Unicaja Banco.
"""

import requests
from app.unicaja_services_config import UnicajaServicesConfig
from qgdiag_lib_arquitectura import CustomLogger


logger = CustomLogger("Servicio para cálculo de gastos de tasación.")


class GastosTasacionService:
    """
    Servicio para calcular gastos de tasación de inmuebles.

    Utiliza el simulador hipotecario público para obtener el coste
    de tasación basado en el precio de la vivienda y provincia.
    """

    def __init__(self):
        config = UnicajaServicesConfig()

        # Configuración de la API y OAuth
        self.client_id = config.client_id
        self.client_secret = config.client_secret
        self.token_url = config.url_token_oauth2
        self.api_url = config.api_gastos_tasacion

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

    def _call_simulacion_service(self, token, params):
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        response = requests.post(self.api_url, headers=headers, json=params)

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

    def call(
        self,
        precio_vivienda: int,
        provincia: str,
        indicador_vivienda_habitual: str,
        tipo_vivienda: int,
        fecha_nacimiento: str,
        ingresos: float,
    ):
        response = ""
        gastos_tasacion = 0.0
        try:
            logger.info("Llamada a servicio para consulta de gastos de tasación")
            params = {
                "impVivienda": precio_vivienda,
                "indVivHabitual": indicador_vivienda_habitual,
                "tipoVivienda": tipo_vivienda,
                "provinciaHip": provincia,
                "fechaNacimiento": fecha_nacimiento,
                "ingresosTit1": ingresos,
                "indEmpleadoPublico": "N",
                "codProvincia": provincia,
                "numLlamada": "1",
            }

            token = self._get_oauth_token(self.client_id, self.client_secret)
            response = self._call_simulacion_service(token, params)
            gastos_tasacion = response["datosSimulacion"]["impTasacion"]
        except Exception as e:
            return f"Error: {e}"
        return gastos_tasacion
