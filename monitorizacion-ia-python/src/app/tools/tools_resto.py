"""
Herramientas de LangChain para servicios auxiliares y validaciones.

Incluye tools para verificar DNI/NIE, consultar clientes, gestionar consentimientos
y registrar el log operacional en el sistema.
"""

from typing import Type

from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field, PrivateAttr
import json
from app.constants.global_constants import GlobalConstants

from app.managers.session_adapter import SessionProtocol

from app.models.models_APIRequest import ConsentimientoRequest, LogOperacionalRequest
from app.services.verificar_dni_service import DocumentoIdentidad
from app.services.consulta_consentimiento_service import ConsultaConsentimientoService
from app.services.log_operacional_service import LogOperacionalService
from app.constants.global_constants import GlobalConstants

from qgdiag_lib_arquitectura import CustomLogger

from app.services.tools_logger import LogToolMethod

logger = CustomLogger("Herramientas")


#####################################################################################################
############################# TOOL VERIFICAR DNI Y CONSULTAR CLIENTE ################################
#####################################################################################################
class EzVerificarDNI(BaseTool):
    """Clase base para herramientas de verificación de dni"""

    name: str = "verificar_dni_base_tool"
    description: str = GlobalConstants.BASE_TOOL_DOCSTRING

    _session: SessionProtocol = PrivateAttr()

    def __init__(self, session: SessionProtocol):
        super().__init__()
        self._session = session

    def _run(self, *args, **kwargs):
        """Implementación dummy para tests, no debe usarse en producción"""
        raise NotImplementedError("EzVerificarDNI no debe ejecutarse directamente.")


class VerificarDniInput(BaseModel):
    """
    Modulo para despliegue en dev
    """

    dni_nie: str = Field(description="DNI del usuario")
    acceso_no_clientes: bool = Field(
        description="""True: si se ha accedido desde la operativa NO CLIENTES;
        False: si se ha accedido desde la ficha de un cliente, """
    )
    segundo_interviniente: bool = Field(
        description="""True: si se está consultando la información para el segundo interviniente;
        False: si se está consultando la información para el primer interviniente"""
    )


class VerificarDniTool(EzVerificarDNI):
    """
    Herramienta para validar un DNI/NIE y, si es válido, consultar la información del cliente en el sistema.
    Incorpora lógica específica para:
    - Segundos intervinientes: valida el documento pero no consulta datos del cliente.
    - Preclientes (indCliente == "P"): añade un aviso explícito.
    - Operativa de NO CLIENTES: si `acceso_no_clientes=True` y el NIF corresponde a un CLIENTE (indCliente == "C"),
      devuelve un mensaje de bloqueo para impedir continuar con esa operativa.

    La herramienta SOLO debe usarse cuando el usuario proporcione un DNI/NIE completo y válido.
    No admite búsquedas por nombre, apellidos u otros datos.

    Output esperado (`dict`):
      - valido (bool): True si el documento pasa la validación formal.
      - mensaje (str): Mensaje claro del resultado de la validación/consulta.
      - info_cliente (dict | None): Datos del cliente si se consulta y existe.
      - tipo_cliente (str | None): "cliente", "precliente" o None si desconocido.
      - aviso_agente (str | None): Indicaciones accionables para guiar el flujo del agente.
    """

    name: str = "consultar_cliente_por_nif"
    description: str = (
        """
        Valida un DNI/NIE y, si es válido y no es segundo interviniente, consulta la información del cliente.
        SOLO se usa cuando el usuario proporcione un DNI/NIE completo (no admite búsquedas por nombre/apellidos).
        Si el resultado indica PRECLIENTE (indCliente == "P"), añade un aviso informativo.
        Si `acceso_no_clientes=True` y el NIF corresponde a un CLIENTE (indCliente == "C"), devuelve un mensaje de
        bloqueo para impedir continuar la operativa de NO CLIENTES.
        Devuelve un JSON con:
          - valido, mensaje, info_cliente (si disponible),
          - tipo_cliente: "cliente" | "precliente" | None,
          - aviso_agente: texto breve y accionable.
        """
    )
    args_schema: Type[BaseModel] = VerificarDniInput
    return_direct: bool = False
    _session: SessionProtocol = PrivateAttr()

    def __init__(self, session: SessionProtocol):
        super().__init__(session)

    def _run(
        self,
        dni_nie: str,
        acceso_no_clientes: bool = False,
        segundo_interviniente: bool = False,
    ):
        """
        Ejecuta la verificación del DNI/NIE y gestiona la consulta de cliente según contexto.

        Comportamiento:
          1) Valida formato y letra del documento.
          2) Si `segundo_interviniente=True`: no consulta datos del cliente.
          3) Si el documento es válido y se consulta:
             - Si `indCliente == "P"`: marca `tipo_cliente="precliente"` y añade `aviso_agente` informativo.
             - Si `indCliente == "C"` y `acceso_no_clientes=True`: retorna bloqueo para operativa de NO CLIENTES.
             - Si falta `indCliente`: añade `aviso_agente` solicitando confirmación/reintento de consulta.

        Args:
            dni_nie (str): Documento completo (DNI/NIE) del usuario.
            acceso_no_clientes (bool): Activa reglas de bloqueo si el NIF pertenece a cliente (indCliente == "C").
            segundo_interviniente (bool): Si True, no consulta info de cliente aunque el documento sea válido.

        Returns:
            dict: Estructura con `valido`, `mensaje`, `info_cliente` (opcional),
                  `tipo_cliente` ("cliente" | "precliente" | None), y `aviso_agente`.
                  En caso de bloqueo por NO CLIENTES, `valido` puede ser True pero se incluirá
                  un `mensaje`/`aviso_agente` indicando la restricción.

        Raises:
            ValueError: Si el `dni_nie` está vacío o no cumple requisitos mínimos antes de la validación.
            Exception: Cualquier error inesperado se atrapará y se devolverá en `mensaje` con `valido=False`.
        """

        try:
            LogToolMethod.log_initialization(self)

            documento = DocumentoIdentidad(dni_nie)
            resultado = documento.verificar(segundo_interviniente)

            # Si el documento es válido y tenemos info_cliente:
            if (
                resultado.get("valido")
                and not segundo_interviniente
                and acceso_no_clientes
                and resultado.get("tipo_cliente") == "cliente"
            ):
                return (
                    "El DNI proporcionado existe en el sistema y pertenece a un CLIENTE\n"
                    "Se está operando desde el área para NO CLIENTES\n"
                    "Explícaselo al usuario amablemente y pídele que introduzca otro NIF de un no cliente."
                )

            # En el resto de casos, devolvemos el resultado normal:
            return resultado

        except Exception as e:
            mensaje = {
                "valido": False,
                "mensaje": f"Error interno al verificar/consultar el documento: {str(e)}",
                "info_cliente": None,
                "tipo_cliente": None,
                "aviso_agente": "No se pudo completar la verificación. Solicita reintentar o revisar el documento.",
            }
            LogToolMethod.log_failure(self, mensaje)
            return mensaje 


#####################################################################################################
########################### TOOL PARA CONSULTA CONSENTIMIENTO #######################################
#####################################################################################################
class EzConsultarConsentimiento(BaseTool):
    """Clase base para herramientas de la consulta del consentimiento."""

    name: str = "consultar_consentimiento_base_tool"
    description: str = GlobalConstants.BASE_TOOL_DOCSTRING

    _session: SessionProtocol = PrivateAttr()

    def __init__(self, session: SessionProtocol):
        super().__init__()
        self._session = session

    def _run(self, *args, **kwargs):
        """Implementación dummy para tests, no debe usarse en producción"""
        raise NotImplementedError(
            "EzConsultarConsentimiento no debe ejecutarse directamente."
        )


class ConsultarConsentimientoInput(BaseModel):
    """
    Esquema de entrada para lanzar una solicitud de consentimiento.
    Contiene los datos para el body de la solicitud en un objeto de tipo ConsentimientoRequest.
    """

    datos: ConsentimientoRequest = Field(
        description="Objeto con los datos de cliente requeridos para la consulta del consentimiento."
    )


class ConsultarConsentimientoTool(EzConsultarConsentimiento):
    """
    Consulta el consentimiento de un cliente a partir de sus datos identificativos.
    Utiliza esta tool cuando necesites verificar si el cliente ha otorgado consentimiento.
    """

    name: str = "consultar_consentimiento"
    description: str = (
        """
        Consulta el consentimiento de un cliente a partir de sus datos identificativos.
        Utiliza esta tool cuando necesites verificar si el cliente ha otorgado consentimiento.
        
        Args:
            Modelo de datos ConsentimientoRequest
        Return:
            Debes informar al usuario sobre el resultado de la llamada. Esto incluye:
        - Si el cliente ya tiene el consentimiento aceptado, informa al usuario que el cliente ya ha otorgado su 
        consentimiento.
        - Si el cliente no tiene el consentimiento aceptado, informa al usuario que se ha enviado un correo electrónico
        al cliente para que acepte el consentimiento.
        - En caso de que ocurra un error durante la consulta, informa al usuario sobre el problema y solicita que se 
        revise la información proporcionada.
        
        """
    )
    args_schema: Type[BaseModel] = ConsultarConsentimientoInput
    return_direct: bool = False
    _session: SessionProtocol = PrivateAttr()

    def __init__(self, session: SessionProtocol):
        super().__init__(session)

    def _run(self, datos: ConsentimientoRequest):
        try:
            LogToolMethod.log_initialization(self)

            headers = self._session.get_context().headers
            service = ConsultaConsentimientoService(headers=headers)
            resultado = service.call(datos)

            return resultado

        except Exception as e:
            mensaje = {"error": f"Error al consultar el consentimiento: {str(e)}"}
            LogToolMethod.log_failure(self, mensaje)
            return mensaje 


#####################################################################################################
################################ TOOL PARA LOG OPERACIONAL ##########################################
#####################################################################################################
class EzLogOperacional(BaseTool):
    """Clase base para herramientas de log operacional"""

    name: str = "log_operacional_base_tool"
    description: str = GlobalConstants.BASE_TOOL_DOCSTRING

    _session: SessionProtocol = PrivateAttr()

    def __init__(self, session: SessionProtocol):
        super().__init__()
        self._session = session

    def _run(self, *args, **kwargs):
        """Implementación dummy para tests, no debe usarse en producción"""
        raise NotImplementedError("EzLogOperacional no debe ejecutarse directamente.")


class LogOperacionalInput(BaseModel):
    """
    Esquema de entrada para registrar el log opreacional.
    El parámetro es un objeto de datos de tipo  los datos para el body de la solicitud.
    """

    datos: LogOperacionalRequest = Field(
        description="Objeto con los datos de cliente requeridos para registrar el log operacional."
    )


class LogOperacionalTool(EzLogOperacional):
    """
    Herramienta para registrar el log operacional.
    Utiliza esta tool cuando necesites registrar una acción en el log operacional.
    """

    name: str = "log_operacional"
    description: str = (
        """
        Herramienta para registrar el log operacional.
        Utiliza esta tool cuando necesites registrar una acción en el log operacional.
        
        Args:
            Modelo de datos ConsentimientoRequest
        """
    )
    args_schema: Type[BaseModel] = LogOperacionalInput
    return_direct: bool = False
    _session: SessionProtocol = PrivateAttr()

    def _run(self, datos: LogOperacionalRequest):
        try:
            LogToolMethod.log_initialization(self)

            service = LogOperacionalService()
            resultado = service.call(datos)

            return resultado

        except Exception as e:
            mensaje = {"error": f"Error al consultar el consentimiento: {str(e)}"}
            LogToolMethod.log_failure(self, mensaje)
            return mensaje 
