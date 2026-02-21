"""APP GLOBAL CONSTANTS"""


class GlobalConstants:
    """Global Constants"""

    # ENDPOINTS
    # RESPONSES MESSAGES
    MESSAGE_EXECUTE_ENDPOINT_PROCESS_200_SUCCESS = "Procesado correctamente"
    MESSAGE_401_UNAUTHORIZED = "Token de autenticación inválido o expirado"
    MESSAGE_403_FORBIDDEN = "No dispone de permisos para realizar esta operación"
    MESSAGE_404_NOT_FOUND = "El recurso solicitado no existe"
    MESSAGE_422_VALIDATION_ERROR = "Error de validación en los datos enviados"
    MESSAGE_500_INTERNAL_SERVER_ERROR = "Error interno procesando Bastanteo"
    MESSAGE_503_SERVICE_UNAVAILABLE = "El servicio está temporalmente fuera de servicio"

    # TOOL DESCRIPTION
    BASE_TOOL_DOCSTRING = (
        "Esto es únicamente una base tool. No se debe utilizar como tool"
    )

    # BASTANTEO PROCESS CONSTANTS

    ERROR_DB = "DB error"
