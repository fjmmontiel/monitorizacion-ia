"""
Herramientas de LangChain para gestión y guardado de muestras de interés.

Incluye funciones helper y tools para validar, procesar y registrar muestras de interés de productos hipotecarios
en el sistema.
"""

from typing import Type, List, Optional
import json
import uuid
import re
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field, PrivateAttr

from app.constants.global_constants import GlobalConstants

from app.managers.session_adapter import SessionProtocol
from app.managers.managers import DataMuestraInteresManager
from app.managers.items import EzDataMuestraInteres
from datetime import datetime, timezone

from app.repositories.sqlserver.session_dao import SessionDAO
from app.models.models_APIRequest import LogOperacionalRequest
from app.constants.global_constants import GlobalConstants
from app.models.models import (
    DatosPreEval,
    DatosOperacion,
    DatosIntervSimple,
    DatosInterv,
    TL,
)
from app.models.models_APIRequest import (
    MuestraInteresRequests,
    ParametrosMuestraDeInteres,
)
from qgdiag_lib_arquitectura import CustomLogger

from app.managers.session_manager import Session
from app.repositories.sqlserver.session_dao import SessionDAO
from app.services.muestra_de_interes_service import MuestraDeInteresService
from app.services.muestra_de_interes_service_documento import DocMuestraDeInteresService
from app.services.muestra_de_interes_service_cancelacion import (
    CancelacionMuestraDeInteresService,
)

from app.services.log_operacional_service import LogOperacionalService
import xml.etree.ElementTree as ET

from app.services.tools_logger import LogToolMethod

logger = CustomLogger("Herramientas")
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

# --- HELPERS PARA GUARDAR UNA MUESTRA DE INTERÉS ---


def log_info(content, session_id):
    """
    Funcion para el log_info
    """
    logger.info(f"SESSION_ID=#{session_id}# {content}")


def parsear_fecha(cadena_fecha):
    """
    Esta función convierte una cadena con el formato "%Y-%m-%d %H:%M:%S"
    a un objeto de tipo datetime.

    Args:
        cadena_fecha (str): La cadena que representa una fecha y hora en el formato "%Y-%m-%d %H:%M:%S".

    Returns:
        datetime: Un objeto de tipo datetime que representa la fecha y hora.
    """
    try:
        # Convertir la cadena a un objeto datetime utilizando strptime
        fecha_hora = datetime.strptime(cadena_fecha, DATETIME_FORMAT)
        return fecha_hora
    except ValueError:
        # En caso de que la cadena no tenga el formato correcto, ponemos la fecha actual para evitar el error
        return datetime.now()


def obtener_hora_actual():
    """
    Esta función devuelve la hora actual en el formato YYYY:MM:DD_HH:mm:ss.

    Utiliza la biblioteca datetime para obtener la fecha y hora actuales y luego las formatea según
    el formato especificado.

    Returns:
        str: La hora actual en el formato YYYY-MM-DD HH:mm:ss.
    """
    # Obtener la fecha y hora actuales
    ahora = datetime.now()

    # Formatear la fecha y hora según el formato especificado
    hora_formateada = ahora.strftime(DATETIME_FORMAT)

    return hora_formateada


def calcular_tiempo_transcurrido(timestamp: str):
    """
    Funcion para calcular_tiempo_transcurrido
    """
    inicio = parsear_fecha(timestamp)
    ahora = parsear_fecha(obtener_hora_actual())
    diferencia = ahora - inicio
    return diferencia.total_seconds()


def actualizar_sesion(
    id_sesion: str, timestamp: str, mensaje: str, centro: str, session_metrics: Session
):
    """
    Funcion para actualizar_sesion
    """
    segundos = calcular_tiempo_transcurrido(timestamp)
    log_info(f"{mensaje}. Tiempo transcurrido: {segundos}", id_sesion)
    session_metrics.muestra_de_interes += 1
    session_metrics.centro = centro
    session_metrics.actualizar()
    SessionDAO().update_session(session_metrics)


def registrar_log_operacional(
    headers: dict,
    id_usuario: str,
    id_sesion: str,
    time_inicio: str,
    time_fin: str,
    resultado: dict,
):
    """Función para registrar el log operacional"""
    try:
        data_log_operacional = {
            "codGestor": id_usuario,
            "timestampInicio": time_inicio,
            "timestampFin": time_fin,
            "claper": "BBB03333",
            "httpMethod": "GET",
            "modulo": "OPERACIONES",
            "seccion": "HIPOTECAS",
            "operacion": "CREAR_MUESTRA_INTERES",
            "path": "/pudgc-portal-gestor-ms-administracion/gestores/cartera/PG014602",
            "request": None,
            "response": f"{resultado}",
            "status": "200",
        }
        objeto_data_log_operacional = LogOperacionalRequest(**data_log_operacional)
        service = LogOperacionalService(headers=headers)
        resultado_log_operacional = service.call(objeto_data_log_operacional)

        # Verificar si hubo error en el log operacional
        if (
            isinstance(resultado_log_operacional, dict)
            and "error" in resultado_log_operacional
        ):
            log_info(
                f"Error en el log operacional (no crítico): {resultado_log_operacional['error']}",
                id_sesion,
            )
        else:
            log_info(
                f"Log operacional registrado: {resultado_log_operacional}",
                id_sesion,
            )
    except Exception as e:
        log_info(f"Error general la registrar el log operacional: {str(e)}", id_sesion)


def recuperar_doc_muestra_interes(id_sesion, resultado):
    """Función para recuperar el documento de muestra de interés"""
    try:
        if "numExpeSG" not in resultado:
            log_info(
                "Error: numExpeSG no encontrado en resultado.",
                id_sesion,
            )
            resultado["documento"] = None

        else:
            num_expediente_sg = resultado["numExpeSG"]
            num_expediente = f"{num_expediente_sg['anyo']}{num_expediente_sg['centro']}{num_expediente_sg['idExpe']}"
            doc_response = DocMuestraDeInteresService().call(
                num_expediente=num_expediente
            )
            if isinstance(doc_response, dict) and "error" in doc_response:
                resultado["documento"] = None
                return resultado, doc_response
            else:
                root = ET.fromstring(doc_response)
                url_pdf = root.find(".//{*}URL-PDF").text
                resultado["documento"] = url_pdf
    except Exception as doc_error:
        log_info(f"Error al obtener documento: {str(doc_error)}", id_sesion)
        resultado["documento"] = None
    return resultado, None


def llamar_servicio_muestra_de_interes(
    headers: dict,
    datos_preeval_completo: DatosPreEval,
    datos_operacion_completo: DatosOperacion,
    list_datos_interv_completo: List[DatosInterv],
    centro: str,
    id_usuario: str,
    id_sesion: str,
    timestamp: str,
    session_metrics: Session,
):
    """
    Funcion para llamar_servicio_muestra_de_interes
    """
    resultado = None  # Inicializar para control de errores

    tl = TL(
        datosPreEval=datos_preeval_completo,
        datosOperacion=datos_operacion_completo,
        datosInterv=list_datos_interv_completo,
    )
    api_request = MuestraInteresRequests(
        tl=tl,
        indLlamada="O",
        indAccion="ALTA",
        centro=centro,
        usuario=id_usuario,
    )

    try:
        time_inicio = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        json_obj = api_request.model_dump(exclude_none=True)
        resultado = MuestraDeInteresService().call(json_obj)
        # Añadimos el id_sesion al resultado para trazabilidad
        resultado["id_sesion"] = id_sesion
        error_doc = None

        time_fin = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        if "error" in resultado:
            if "exec cics invoke webserv" in str(
                resultado
            ) or "Servicio no disponible momentáneamente" in str(resultado):
                actualizar_sesion(
                    id_sesion,
                    timestamp,
                    """Se ha llegado hasta el guardado de la muestra de interés, pero no se ha podido guardar por un 
                    error del sistema""",
                    centro,
                    session_metrics,
                )
                return {
                    "error": "Los datos son correctos, pero el servicio no está disponible temporalmente."
                }
            else:
                log_info(
                    f"Error al guardar la muestra de interés: {resultado.get('error')}",
                    id_sesion,
                )
                return {"error": f"{resultado}"}
        else:
            # Se obtiene el número de expediente para recuperar el DOC
            resultado, error = recuperar_doc_muestra_interes(id_sesion, resultado)
            error_doc = error
            actualizar_sesion(
                id_sesion,
                timestamp,
                "Muestra de interés guardada correctamente",
                centro,
                session_metrics,
            )
            registrar_log_operacional(
                headers, id_usuario, id_sesion, time_inicio, time_fin, resultado
            )

    except Exception as e:
        log_info(
            f"Error general en llamar_servicio_muestra_de_interes: {str(e)}", id_sesion
        )
        # Si ya tenemos resultado del servicio principal, lo devolvemos aunque haya errores secundarios
        if resultado is not None:
            log_info(
                "Devolviendo resultado principal a pesar del error.",
                id_sesion,
            )
            return resultado
        return {"error": str(e)}

    if error_doc:
        resultado["documento"] = error_doc
        resultado["mensaje"] = (
            "La muestra de interés se guardó correctamente, pero hubo un problema al generar el documento asociado."
        )
    else:
        resultado["mensaje"] = (
            """La muestra de interés se guardó correctamente y el documento se ha generado con éxito.
            No muestres el enlace del documento en el chat."""
        )
    return resultado


#####################################################################################################
############################ TOOL PARA GUARDAR MUESTRA DE INTERES ###################################
#####################################################################################################


class EzGuardarMuestraDeInteres(BaseTool):
    """Clase base para herramientas para guardar la muestra de interes"""

    name: str = "guardar_muestra_de_interes_base_tool"
    description: str = GlobalConstants.BASE_TOOL_DOCSTRING

    _session: SessionProtocol = PrivateAttr()

    def __init__(self, session: SessionProtocol):
        super().__init__()
        self._session = session

    def _run(self, *args, **kwargs):
        """Implementación dummy para tests, no debe usarse en producción"""
        raise NotImplementedError(
            "EzGuardarMuestraDeInteres no debe ejecutarse directamente."
        )


class GuardarMuestraDeInteresInput(BaseModel):
    """
    Esquema de entrada para guardar una muestra de interés.
    """

    nombre: str = Field(
        description="""Nombre que recibe la muestra de interés. Se debe utilizar un nombre amigable
                        como 'Muestra de interés 1' e incrementar el número si se crean más"""
    )

    datos: ParametrosMuestraDeInteres = Field(
        description="Objeto que contiene los datos necesarios para guardar la muestra de interés"
    )


class GuardarMuestraDeInteresTool(EzGuardarMuestraDeInteres):
    """
    Guarda una muestra de interés de un producto hipotecario en el sistema utilizando los datos proporcionados.
    Args:
        - confirmacion_usuario (bool): Indica si el usuario ha validado que todos los datos (preevaluación,
        - operación e interviniente) son correctos y ha confirmado que quiere guardar la muestra de interés.
        - centro (str): Identificador del centro u oficina.
        - id_usuario (str): Identificador del usuario que realiza la acción.
        - datos_preeval (DatosPreEvalSimple): Datos de la preevaluación del producto.
        - datos_operacion (DatosOperacionSimple): Datos de la operación hipotecaria.
        - id_sesion (str): Identificador de la sesión actual.
        - timestamp (str): Marca temporal de la operación.

    Returns:
        dict: Resultado de la operación, o un diccionario con el campo "error" si algo falla.
    """

    name: str = "guardar_muestra_de_interes"
    description: str = (
        "Almacena los datos de una muestra de interés identificada por 'nombre' en el panel de contexo."
    )
    args_schema: Type[BaseModel] = GuardarMuestraDeInteresInput
    return_direct: bool = False
    _session: SessionProtocol = PrivateAttr()

    def _run(
        self,
        nombre: Optional[str] = None,
        datos: Optional[ParametrosMuestraDeInteres] = None,
    ):
        LogToolMethod.log_initialization(self)
        if not nombre:
            return {
                "error": "No se ha proporcionado un nombre para la muestra de interés."
            }

        if not datos:
            return {
                "error": f"No se han proporcionado datos para guardar la muestra de interés'{nombre}'."
            }
        # Se recupera el manager de muestra de interes
        manager: DataMuestraInteresManager = self._session.get_manager(
            "muestraInteresManager"
        )

        # EzDataMuestraInteres en memoria
        datos_dict = datos.model_dump()
        parametros_muestra_esta_llamada: ParametrosMuestraDeInteres = (
            ParametrosMuestraDeInteres(**datos_dict)
        )

        try:
            # Usar el contexto distribuido actual
            distributed_context = self._session.get_context()
            session_metrics = distributed_context.get_session_metrics()
            session_metrics.ultima_llamada_guardar_muestra_de_interes = (
                parametros_muestra_esta_llamada
            )
        except Exception as e:
            # Fallback al método anterior
            log_info(
                f"Error usando contexto distribuido para guardar parámetros, usando fallback: {str(e)}",
                datos.id_sesion,
            )

        logger.info(
            f"SESSION_ID=#{datos.id_sesion}# Ejecutando tool guardar_muestra_de_interes"
        )

        # Validación unificada
        error = self._validar_campos_principales(datos)
        if error:
            LogToolMethod.log_failure(self, error)
            return error

        datos_preeval_completo: DatosPreEval = None
        datos_operacion_completo: DatosOperacion = None
        list_datos_interv_completo: List[DatosInterv] = []
        try:
            # Validar preevaluación
            errores_preeval = datos.datosPreEval.validar()
            if errores_preeval:
                return {"errores_preeval": errores_preeval}

            # Validar operación (con referencia a la preeval)
            is_valid, errores_operacion = datos.datosOperacion.validar()
            warnings_operacion = datos.datosOperacion.validar_tasacion(
                datos.datosPreEval.valorTasa
            )
            if not is_valid and errores_operacion:
                return {"errores_operacion": errores_operacion}

            # Si todo está correcto, construir objetos completos
            datos_preeval_completo = datos.datosPreEval.get_full_object()
            datos_operacion_completo = datos.datosOperacion.get_full_object()
            list_datos_interv_completo = self._procesar_intervinientes(
                datos.datosInterv
            )

        except Exception as e:
            mensaje = {"error": str(e)}
            LogToolMethod.log_failure(self, mensaje)
            return mensaje

        # Recuperación de headers
        headers = self._session.get_context().headers
        # Llamada al servicio externo
        resultado = llamar_servicio_muestra_de_interes(
            headers=headers,
            datos_preeval_completo=datos_preeval_completo,
            datos_operacion_completo=datos_operacion_completo,
            list_datos_interv_completo=list_datos_interv_completo,
            centro=datos.centro,
            id_usuario=datos.id_usuario,
            id_sesion=datos.id_sesion,
            timestamp=datos.timestamp,
            session_metrics=session_metrics,
        )
        if warnings_operacion:
            resultado["warnings"] = warnings_operacion
        # Validación básica del resultado
        if not isinstance(resultado, dict):
            return {"error": f"Resultado inesperado del servicio: {resultado}"}

        # Genera un identificacdor un UUID único para el nombre del item.
        id = str(uuid.uuid4())
        try:
            # Si el resultado contiene solo error, forzar excepción
            if "error" not in resultado:
                edmi = EzDataMuestraInteres(nombre, id, resultado)
                manager.add_item(edmi)

        except Exception as e:
            # Añadimos un mensaje simple para informar al agente
            resultado["panel_contexto_status"] = (
                f"No se pudo añadir la muestra de interés al panel de contexto: {str(e)}"
            )

        # Si todo va bien, añadimos mensaje positivo
        if "panel_contexto_status" not in resultado:
            resultado["panel_contexto_status"] = (
                "Muestra de interés añadida correctamente al panel de contexto"
            )

        return resultado

    def _validar_campos_principales(
        self, datos: ParametrosMuestraDeInteres
    ) -> Optional[str]:
        """
        Valida que los campos principales y las condiciones mínimas estén informados.
        Devuelve un mensaje de error si algo falla, o None si todo está correcto.
        """

        # --- Validación de campos obligatorios ---
        campos_principales = {
            "centro": datos.centro,
            "id_usuario": datos.id_usuario,
            "datosPreEval": datos.datosPreEval,
            "datosOperacion": datos.datosOperacion,
            "datosInterv": datos.datosInterv,
            "id_sesion": datos.id_sesion,
            "timestamp": datos.timestamp,
        }

        errores = [f"Falta {n}" for n, valor in campos_principales.items() if not valor]

        if errores:
            return f"Algunos campos requeridos no están informados:\n{chr(10).join(errores)}."

        # --- Validación de confirmación del usuario ---
        if not datos.usuario_ha_validado_la_informacion:
            return (
                "El usuario debe confirmar todos los datos antes de guardar la muestra de interés.\n"
                "Muestra todos los datos recogidos: Datos de Preevaluación, Datos Operación, Datos Interviniente."
            )

        # --- Validación de centro ---
        if datos.centro in ("", "NNNN"):
            return "El código de centro es incorrecto. Solicítaselo al usuario."

        # --- Validación de id_usuario ---
        if datos.id_usuario in ("", "U......"):
            return "El identificador de usuario es incorrecto. Solicítaselo al usuario."

        return None

    def _procesar_intervinientes(self, datos_interv: List[DatosIntervSimple]):
        """Funcion para procesar_intervinientes"""
        num_interviniente = 1
        list_datos_interv_completo = []
        for interviniente in datos_interv:
            # Usamos el nuevo método validar en lugar de check_campos_obligatorios
            errores_interviniente = interviniente.validar(num_interviniente)

            # Parche para los ingresos
            if (
                interviniente.datos_ingresos.ingresoFijos <= 0
                and "5" not in interviniente.datos_personales_y_profesionales.profesion
            ):
                errores_interviniente.append(
                    f"""Los ingresos del interviniente no pueden ser cero para la 
                    ""profesión {interviniente.datos_personales_y_profesionales.profesion}"""
                )

            # Parche para la fecha de antigüedad de los parados
            if "5" in interviniente.datos_personales_y_profesionales.profesion and (
                interviniente.datos_personales_y_profesionales.fechaAntEmpresa is None
                or interviniente.datos_personales_y_profesionales.fechaAntEmpresa == ""
            ):
                interviniente.datos_personales_y_profesionales.fechaAntEmpresa = (
                    "2024-01-01"  # PONEMOS UNA FECHA CUALQUIERA
                )

            # Comprobamos si hay errores en la lista
            if errores_interviniente:
                # Convertimos la lista de errores en un mensaje de error unido por saltos de línea
                errores_msg = "\n".join(errores_interviniente)
                raise ValueError(
                    f"""Se han detectado los siguientes errores en los datos del 
                    interviniente {num_interviniente}:\n{errores_msg}"""
                )

            list_datos_interv_completo.append(
                interviniente.get_full_object().model_dump(exclude_none=True)
            )
            num_interviniente += 1

        return list_datos_interv_completo


#####################################################################################################
############################ TOOL PARA CANCELAR UNA MUESTRA DE INTERES ##############################
#####################################################################################################
class EzCancelarMuestraDeInteres(BaseTool):
    """Clase base para herramientas de la consulta del consentimiento."""

    name: str = "cancelar_muestra_de_interes_base_tool"
    description: str = GlobalConstants.BASE_TOOL_DOCSTRING

    _session: SessionProtocol = PrivateAttr()

    def __init__(self, session: SessionProtocol):
        super().__init__()
        self._session = session

    def _run(self, *args, **kwargs):
        """Implementación dummy para tests, no debe usarse en producción"""
        raise NotImplementedError(
            "EzCancelarMuestraDeInteres no debe ejecutarse directamente."
        )


class CancelarMuestraDeInteresInput(BaseModel):
    """
    Esquema de entrada para cancelar una muestra de interés en el sistema.
    Se debe pasar como parámetro el número de expediente asociado a la muestra de interés.
    """

    nombre: str = Field(
        description="Nombre de la muestra de interés que se quiere cancelar."
    )


class CancelarMuestraDeInteresTool(EzCancelarMuestraDeInteres):
    """
    Esta herramienta permite cancelar una muestra de interés en cualquier momento.

    Utiliza esta tool cuando necesites cancelar una muestra de interés.
    """

    name: str = "cancelar_muestra_de_interes"
    description: str = (
        """
        Esta herramienta permite cancelar una muestra de interés en cualquier momento.
        Utiliza esta tool cuando necesites cancelar una muestra de interés.
        
        Args:
            nombre: Nombre de la muestra de interés que se quiere cancelar.
        Return:
            Debes informar al usuario sobre el resultado de la llamada. Si la muestra no se ha podido cancelar
            correctamente, informa al usuario sobre el error.
        """
    )
    args_schema: Type[BaseModel] = CancelarMuestraDeInteresInput
    return_direct: bool = False
    _session: SessionProtocol = PrivateAttr()

    def __init__(self, session: SessionProtocol):
        super().__init__(session)

    def _run(self, nombre: str):
        try:
            LogToolMethod.log_initialization(self)

            manager: DataMuestraInteresManager = self._session.get_manager(
                "muestraInteresManager"
            )
            item_muestra = manager.get_item(nombre)
            num_expediente = (
                item_muestra.data["numExpeSG"]["anyo"]
                + item_muestra.data["numExpeSG"]["centro"]
                + item_muestra.data["numExpeSG"]["idExpe"]
            )

            if not re.match(r"^\d{16}$", num_expediente):
                return {
                    "error": "El número de expediente debe tener el formato 'AAAA-CCCC-IDEXPE'."
                }

            service = CancelacionMuestraDeInteresService()
            resultado = service.call(num_expediente=num_expediente)

            return resultado

        except Exception as e:
            mensaje = {"error": f"Error al cancelar la muestra de interés: {str(e)}"}
            LogToolMethod.log_failure(self, mensaje)
            return mensaje
