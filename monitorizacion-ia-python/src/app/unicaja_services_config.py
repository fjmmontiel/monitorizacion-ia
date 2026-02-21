"""
Modulo para despliegue en dev
"""

from app.settings import settings


class UnicajaServicesConfig:
    """
    Modulo para despliegue en dev
    """

    # CAMBIAR
    def __init__(self):
        # Configuración de la API y OAuth. DESARROLLO
        self.client_id = settings.CLIENT_ID_HIPOTECA_DIGITAL
        self.client_secret = settings.CLIENT_SECRET_HIPOTECA_DIGITAL
        self.url_token_oauth2 = settings.URL_TOKEN_OAUTH
        self.token_jwt = settings.URL_TOKEN_JWT

        self.url_token_log_operacional = settings.URL_TOKEN_LOG_OPERACIONAL
        self.api_consulta_cliente_url = settings.API_CONSULTA_CLIENTE
        self.api_muestra_interes_url = settings.API_MUESTRA_INTERES
        self.api_cancelar_muestra_interes_url = settings.API_CANCELAR_MUESTRA_INTERES
        self.api_doc_muestra_interes_url = settings.API_DOC_MUESTRA_INTERES
        self.api_consulta_consentimiento = settings.API_CONSULTA_CONSENTIMIENTO
        self.api_bonificaciones = settings.API_BONIFICACIONES
        self.api_log_operacional = settings.API_LOG_OPERACIONAL
        self.api_simular_precios = settings.API_SIMULAR_PRECIOS
        self.api_gastos_hipotecarios = settings.API_GASTOS_HIPOTECARIOS
        self.api_gastos_tasacion = settings.API_GASTOS_TASACION

        # Credenciales log operacional
        self.client_id_log_operacional = settings.CLIENT_ID_LOG_OPERACIONAL
        self.client_s_log_operacional = settings.CLIENT_SECRET_LOG_OPERACIONAL

    # Getters
    def get_client_id(self):
        return self.client_id

    def get_client_secret(self):
        return self.client_secret

    def get_token_url(self):
        return self.token_jwt
