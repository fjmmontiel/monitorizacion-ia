"""
Servicio principal de LLM y agente conversacional para hipotecas.

Proporciona la funcionalidad central del chatbot de hipotecas, incluyendo
gestión de contexto distribuido, integración con modelos de lenguaje,
herramientas especializadas y procesamiento de conversaciones.
"""

import asyncio
import json
import re
import uuid
import inspect
from datetime import datetime

from typing import List, Optional, Dict, Any

from fastapi import BackgroundTasks
from app.services.chat_helpers import ChatHelpers, procesar_evento

from app.settings import settings

from app.models.models_APIRequest import (
    DatosGastosTasacion,
    DatosGastosEscrituraCompraventa,
    DatosCuotaHipoteca,
)
from app.models.models_helper import get_traduccion_from_db
from app.models.models_fichas import ParametrosCalculoBonificaciones

from app.models.models_fichas import FichaProductoHipoteca, Bonificacion

from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
import httpx

from app.services.gastos_hipotecarios_service import GastosHipotecariosService
from app.services.gastos_tasacion_service import GastosTasacionService
import app.tools.tools_resto as tools_resto
import app.tools.tools_preeval as tools_preeval
import app.tools.tools_operacion as tools_operacion
import app.tools.tools_interv as tools_interv
import app.tools.tools_recomendacion_hipoteca as tools_recomendar_hipoteca
import app.tools.tools_cliente as tools_cliente
import app.tools.tools_gestor as tools_gestor
import app.tools.tools_muestra_interes as tools_muestra_interes

from app.repositories.sqlserver.session_dao import SessionDAO
from app.repositories.sqlserver.database_connector import get_manual_db_session

from app.managers.session_adapter import DistributedSessionAdapter

from qgdiag_lib_arquitectura import CustomLogger
from qgdiag_lib_arquitectura.utilities.ai_core.ai_core import get_ai_core_session


from app.services.prompts.prompts import Prompts
from app.managers.distributed_context import DistributedContext

from app.services.tools_logger import LogToolFunction

AICORE_URL = settings.AICORE_URL
ENGINE_ID = settings.ENGINE_ID
URL_TOKEN_JWT = settings.URL_TOKEN_JWT

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

logger = CustomLogger("llm_service")

# Variable global para el contexto distribuido actual (thread-safe)
_current_distributed_context = None


def set_current_distributed_context(context):
    """Establece el contexto distribuido actual para las herramientas"""
    global _current_distributed_context
    _current_distributed_context = context


def get_current_distributed_context():
    """Obtiene el contexto distribuido actual"""
    global _current_distributed_context
    if not _current_distributed_context:
        raise RuntimeError("No hay contexto distribuido configurado")
    return _current_distributed_context


def generar_identificador_sesion():
    """
    Esta función genera un identificador de sesión único.

    Utiliza la biblioteca uuid para generar un identificador único.
    Un UUID (Identificador Universalmente Único por sus siglas en inglés)
    garantiza unicidad y es altamente improbable que se repita.

    Returns:
        str: Un identificador de sesión en formato de cadena.
    """
    # Genera un UUID utilizando uuid4(), que genera un UUID aleatorio.
    identificador_unico = uuid.uuid4()

    # Conviértelo a una cadena.
    return str(identificador_unico)


async def create_langchain_model(
    aicore_url: str, headers: Dict[str, str]
) -> ChatOpenAI:
    """
    Construye un ChatOpenAI de LangChain apuntando al endpoint OpenAI-compatible de AI Core.
    Reutiliza la sesión (cookies) de ServerClient para que el backend reconozca la sesión.
    """

    access_key, secret_key, server_cookies = await get_ai_core_session(headers)

    http_client = httpx.Client()
    http_client.cookies = server_cookies  # portamos cookies de sesión

    # ChatOpenAI con base OpenAI-compatible de AI Core
    llm = ChatOpenAI(
        model=ENGINE_ID,
        openai_api_key=f"{access_key}:{secret_key}",
        base_url=f"{aicore_url}/model/openai",
        http_client=http_client,
        stream_options={"include_usage": True},
        temperature=0,
        streaming=True,
    )
    return llm


class LangchainLLMService:
    """
    Servicio principal del agente conversacional de hipotecas.

    Gestiona la interacción con modelos de lenguaje, herramientas especializadas
    y el contexto distribuido para proporcionar asistencia integral en procesos
    hipotecarios mediante conversación natural.
    """

    system_prompt = Prompts.SYSTEM_PROMPT

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("placeholder", "{chat_history}"),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}"),
        ]
    )

    def __init__(self):
        """
        Inicializa el LangchainLLMService.
        NOTA: Requiere llamar a set_distributed_context() antes de usar el servicio.
        """
        self.llm = None

        self.distributed_context = None  # Requerido - debe configurarse antes de usar
        self.tools = []  # Se inicializará cuando se configure el contexto distribuido

        # Inicializar otros componentes
        self.message_history = []
        self.session_id = ""

        self.session_dao = SessionDAO()
        # El agente se creará cuando se configure el contexto distribuido
        self.agent = None
        self.agent_executor = None

    async def init_async(self, headers):
        if self.llm is None:
            self.llm = await create_langchain_model(
                aicore_url=AICORE_URL, headers=headers
            )
            self.agent = create_tool_calling_agent(self.llm, self.tools, self.prompt)
            self.agent_executor = AgentExecutor(
                agent=self.agent, tools=self.tools, verbose=settings.VERBOSE
            )
        return self

    def _initialize_tools(self, session_context):
        """
        Inicializa todas las herramientas con el contexto de sesión proporcionado

        Args:
            session_context: SessionProtocol o pseudo-session para contexto distribuido
        """
        # Herramientas de verificación y consulta
        tool_verificar_dni_nie = tools_resto.VerificarDniTool(session_context)
        tool_consultar_consentimiento = tools_resto.ConsultarConsentimientoTool(
            session_context
        )

        # Herramientas para solicitud de recomendación hipotecas
        tool_create_recomendacion_hipotecas = (
            tools_recomendar_hipoteca.CreateRecomendacionHipotecaTool(session_context)
        )
        tool_delete_recomendacion_hipotecas = (
            tools_recomendar_hipoteca.DeleteRecomendacionHipotecaTool(session_context)
        )

        # Herramientas recomendación hipotecas
        tool_negociar_bonificaciones = (
            tools_recomendar_hipoteca.NegociarBonificacionesTool(session_context)
        )
        tool_consultar_promociones = tools_recomendar_hipoteca.ConsultarPromocionTool(
            session_context
        )
        # Herramienta para consultar la información de un producto
        tool_obtener_catalogo_productos = (
            tools_recomendar_hipoteca.ObtenerCatalogoProductosTool(session_context)
        )
        tool_consultar_producto = tools_recomendar_hipoteca.ConsultarProductoTool(
            session_context
        )

        # Herramientas preevaluación
        tool_create_preeval = tools_preeval.CreatePreevalTool(session_context)
        tool_update_preeval = tools_preeval.UpdatePreevalTool(session_context)
        tool_delete_preeval = tools_preeval.DeletePreevalTool(session_context)

        # Herramientas operación
        tool_create_operacion = tools_operacion.CreateOperacionTool(session_context)
        tool_update_operacion = tools_operacion.UpdateOperacionTool(session_context)
        tool_delete_operacion = tools_operacion.DeleteOperacionTool(session_context)

        # Herramientas intervinientes
        tool_create_interv = tools_interv.CreateIntervTool(session_context)
        tool_update_interv = tools_interv.UpdateIntervTool(session_context)
        tool_delete_interv = tools_interv.DeleteIntervTool(session_context)

        # Herramientas datos cliente
        tool_create_cliente = tools_cliente.CreateClienteTool(session_context)

        # Herramientas datos gestor
        tool_create_gestor = tools_gestor.CreateGestorTool(session_context)

        # Herramientas muestra de interes
        tool_guardar_muestra_de_interes = (
            tools_muestra_interes.GuardarMuestraDeInteresTool(session_context)
        )
        tool_cancelar_muestra_de_interes = (
            tools_muestra_interes.CancelarMuestraDeInteresTool(session_context)
        )

        self.tools = [
            # Verificar DNI y consultar cliente
            tool_verificar_dni_nie,
            # Consultar consentimiento
            tool_consultar_consentimiento,
            # Registrar log operacional
            # tool_registrar_log_operacional,
            # Herramientas datos cliente
            tool_create_cliente,
            # Herramientas datos gestor
            tool_create_gestor,
            # Herramientas para solicitud de recomendación hipotecas
            tool_create_recomendacion_hipotecas,
            tool_delete_recomendacion_hipotecas,
            # Herramientas recomendación hipotecas
            # Herramienta para negociar las bonificaciones de base de datos
            tool_negociar_bonificaciones,
            tool_consultar_promociones,
            # Herramientas datos preeavaluación
            tool_create_preeval,
            tool_update_preeval,
            tool_delete_preeval,
            # Herramientas datos operación
            tool_create_operacion,
            tool_update_operacion,
            tool_delete_operacion,
            # Herramientas datos intervinientes
            tool_create_interv,
            tool_update_interv,
            tool_delete_interv,
            # Herramientas de consulta
            get_current_time,
            # Herramienta para inferir situación laboral
            obtener_actividad_economica_empresa,
            # Calcular bonificaciones
            calcular_bonificaciones,
            # Obtener catalogo de productos
            tool_obtener_catalogo_productos,
            tool_consultar_producto,
            guardar_opinion,
            # recomendar_hipotecas,
            tool_guardar_muestra_de_interes,
            tool_cancelar_muestra_de_interes,
            calcular_gastos_escritura_compraventa,
            calcular_gastos_tasacion,
            calcular_cuota_hipoteca,
        ]

        self.session_dao = SessionDAO()

    def set_distributed_context(self, distributed_context: DistributedContext):
        """
        Configura el contexto distribuido para esta instancia del servicio.
        OBLIGATORIO: Debe llamarse antes de usar el servicio.

        Args:
            distributed_context: Instancia de DistributedContext
        """

        self.distributed_context = distributed_context
        self.session_id = distributed_context.session_id

        # Configurar el contexto distribuido globalmente para las herramientas
        set_current_distributed_context(distributed_context)

        # Crear pseudo-session para compatibilidad con herramientas existentes
        self.pseudo_session = DistributedSessionAdapter(self.distributed_context)

        # Inicializar herramientas con el contexto distribuido
        self._initialize_tools(self.pseudo_session)

        # Crear el agente con las herramientas
        self.agent = create_tool_calling_agent(self.llm, self.tools, self.prompt)
        self.agent_executor = AgentExecutor(
            agent=self.agent, tools=self.tools, verbose=settings.VERBOSE
        )

    def get_current_context(self):
        """
        Obtiene el contexto distribuido actual.
        Lanza una excepción si no se ha configurado el contexto distribuido.
        """
        if not self.distributed_context:
            raise RuntimeError(
                "Contexto distribuido no configurado. Llama a set_distributed_context() primero."
            )
        return self.distributed_context

    def log(self, content):
        logger.info(f"SESSION_ID=#{self.get_session_id()}# {content}")

    def save_session(self):
        """Guarda la sesión usando el contexto distribuido"""
        if self.distributed_context:
            self.distributed_context.save_session_metrics()
        else:
            raise RuntimeError(
                "Contexto distribuido no configurado. No se puede guardar la sesión."
            )

    def get_session_id(self):
        if self.session_id == "":
            self.session_id = self.get_session_id_from_messages()
        return self.session_id

    def get_session_id_from_messages(self):
        salida = ""
        if self.message_history is not None and len(self.message_history) > 1:
            # Cogemos el primer mensaje de System:
            cadena: str = self.message_history[1].content
            # Definir el patrón de la expresión regular para encontrar el ID de sesión
            patron = r"\[ID_SESION=([a-f0-9\-]+)\]"

            # Buscar el patrón en la cadena
            coincidencia = re.search(patron, cadena)

            if coincidencia:
                # Si se encuentra una coincidencia, retornar el grupo 1 (el ID de sesión)
                salida = coincidencia.group(1)
            else:
                # Si no se encuentra una coincidencia, retornar None
                salida = ""
        return salida

    def get_codigo_gestor_from_messages(self):
        salida = ""
        if self.message_history is not None:
            # Tomamos el segundo mensaje (o ajusta según tu lógica)
            cadena: str = self.message_history[0].content
            # Patrón para encontrar el código gestor
            patron = r"CODIGO_GESTOR:\s*([A-Z0-9]+)"

            # Buscar el patrón en la cadena
            coincidencia = re.search(patron, cadena)

            if coincidencia:
                salida = coincidencia.group(1)
            else:
                salida = ""
        return salida

    def get_centro_gestor_from_messages(self):
        salida = ""
        if self.message_history is not None:
            # Tomamos el segundo mensaje (o ajusta según tu lógica)
            cadena: str = self.message_history[0].content
            # Patrón para encontrar el código gestor
            patron = r"CENTRO:\s*(\d+)"

            # Buscar el patrón en la cadena
            coincidencia = re.search(patron, cadena)

            if coincidencia:
                salida = coincidencia.group(1)
            else:
                salida = ""
        return salida

    async def chat(self, background_tasks: BackgroundTasks, headers):
        """Función para el chat - Refactorizada"""
        # Validar que el contexto distribuido esté configurado
        if not self.distributed_context:
            raise RuntimeError(
                "Contexto distribuido no configurado. Llama a set_distributed_context() primero."
            )

        if not self.agent_executor:
            raise RuntimeError(
                "AgentExecutor no inicializado. Llama a set_distributed_context() primero."
            )

        # Configuración inicial
        stop_event = asyncio.Event()
        background_tasks.add_task(self.check_client_disconnect, stop_event)

        log_content_container = [""]  # Lista para mantener referencia mutable

        try:
            # Generar mensaje del usuario con contexto
            user_message = ChatHelpers.crear_mensaje_usuario(self)

            # Inicializar sesión si es la primera interacción
            if len(self.message_history) == 1:
                inicializacion = ChatHelpers.inicializar_sesion(self)
                self.message_history.append(HumanMessage(content=inicializacion))
                yield inicializacion

            # Guardar historial de mensajes en la sesion

            # Procesamiento del stream de eventos
            async for event in self.agent_executor.astream_events(
                {"input": user_message, "chat_history": self.message_history},
                version="v1",
            ):
                if stop_event.is_set():
                    self.log("Stream stopped by client")
                    break

                async for output in procesar_evento(
                    self, event, log_content_container, headers
                ):
                    if output:  # Solo yield si hay contenido
                        yield output.replace("\\n", "\n")

        except asyncio.CancelledError:
            self.log("Stream cancelled")
        finally:
            self.log("System chat finished")

    async def check_client_disconnect(self, stop_event: asyncio.Event):
        while not stop_event.is_set():
            try:
                await asyncio.sleep(0.1)
            except asyncio.CancelledError:
                stop_event.set()
                break

    def add_messages(self, messages):
        """Añade mensajes al historial"""
        # Validar que el contexto distribuido esté configurado
        try:
            for message in messages:
                if message["role"] == "user" and message["message"] != "":
                    self.message_history.append(
                        HumanMessage(content=message["message"])
                    )
                elif message["role"] == "bot" and message["message"] != "":
                    self.message_history.append(AIMessage(content=message["message"]))
            self.log("Nuevo mensaje añadido con éxito")
        except Exception as e:
            logger.error(f"Error añadiendo el mensaje: {e}")


@tool("obtener_actividad_economica_empresa")
async def obtener_actividad_economica_empresa(profesion: str, empresa: str):
    """
    Esta herramienta permite inferir la actividad económica a partir de la profesión y la empresa en la que trabaja
    el cliente. La herramienta requiere que se pasen los nombres de la profesión y la empresa como parámetros.
    No se deben pasar los códigos directamente.

    Args:
        profesion (str): Profesion del cliente.
        empresa (str): Empresa en la que trabaja el cliente.

    Returns:
        str: La actividad económica y su código correspondiente asociados a la información laboral dada.
    """
    tool_name = inspect.currentframe().f_code.co_name
    LogToolFunction.log_initialization(tool_name)

    act_economica_desc = get_traduccion_from_db("IAG_TRD_SECTOR_ACTIVIDAD")

    # Probar que versión de llamada a la api funciona, si esta o la siguiente
    response = f"""
    Infiere la actividad económica según la información disponible y actuando de la siguiente manera:
    Actua como un experto en, dada una información sobre cliente, clasificar la información usando una serie de 
    códigos dados. Siempre mantienes la coherencia y nunca devuelves códigos que no te hayan indicado previamente.
    Dada la siguiente profesion de una persona '{profesion}' desempeñada en la empresa '{empresa}', 
    infiere la actividad económica a partir de la empresa en la que trabaja. 
        - Por ejemplo: Un abogado en Repsol --> Actividad económica = Energía y Agua=1C
        - Otro ejemplo: Un abogado en Iberia --> Actividad económica = Agencias de Viaje=2R
    Las opciones disponibles y su correspondiente código las tienes en '{act_economica_desc}'
    Responde solo con el nombre de la actividad económica correcta seguido del código asociado. 
    Llama a la herramienta `update_interviniente` para actualizar el dato inferido en el panel de contexto.
    Informa al usuario de la actividad economica inferida. Está prohibido continuar sin la confirmación explícita
    Si el usuario no está de acuerdo, facilita el catálogo con la traducción de códigos para acordar la actividad 
    económica y así actualizar la información del interviniente utilizando la herramienta `update_interviniente`. 
    """

    return response


def extraer_tasas(texto):
    """
    Funcion para extraer las tasas
    """
    # Expresión regular para identificar todas las tasas de interés
    patron = r"(\d+,\d+)"

    # Buscar todas las coincidencias de tasas de interés en el texto
    tasas = re.findall(patron, texto)

    # Convertir las tasas de interés encontradas de cadena a float
    tasas = [float(tasa.replace(",", ".")) for tasa in tasas]

    # Verificar cuántas tasas encontramos
    if len(tasas) < 4:
        # Si encontramos menos de 4 tasas, duplicamos la primera tasa para simplificar 'primeros periodo'
        tasas.insert(1, tasas[0])

    return tasas


@tool("calcular_bonificaciones", args_schema=ParametrosCalculoBonificaciones)
async def calcular_bonificaciones(
    codigo_administrativo: Optional[str] = None,
    grupo_adquisicion: Optional[str] = None,
    bonificaciones: Optional[List[Bonificacion]] = None,
):
    """
    Se utiliza para obtener los tipos de interés bonificados para un producto, un grupo de adquisión y una lista
    de bonficaciones.
    Imprescindible: siempre que llames a esta herramienta debes pasar los siguientes parámetros:
        - 'codigo_administrativo': El código administrativo del producto seleccionado.
        - 'grupo_adquisicion': El grupo de adquisición correspondiente al producto. Esto debe ser extraído de la
        información sobre la finalidad de adquisión del inmueble. Los valores posibles son:
            - 'grupo_adquisicion_vivienda_1' -> Adquisición de vivienda para residencia habitual
            - 'grupo_adquisicion_vivienda_2' -> Adquisición de vivienda para segunda residencia
            - 'grupo_no_adquisicion_vivienda' -> Otros
        - 'bonificaciones': Una lista de objetos de tipo `Bonificacion`, donde cada objeto debe incluir:
            - 'nombre': El nombre de la bonificación seleccionada por el usuario.
            - 'valor': El valor de la bonificación en puntos porcentuales, que debe ser extraído de la información
            de las bonificaciones disponibles para el producto.
    """
    tool_name = inspect.currentframe().f_code.co_name
    LogToolFunction.log_initialization(tool_name)

    # 1. Validación de datos
    errores = _validar_parametros(
        codigo_administrativo, grupo_adquisicion, bonificaciones
    )
    if errores:
        return {
            "error": "Hay errores en los datos de entrada de la herramienta calcular_bonificaciones:\n"
            + errores
        }

    # 2. Consulta de producto
    producto_dict = _obtener_producto_dict(codigo_administrativo)
    if producto_dict is None:
        return None

    # 3. Extracción de tarifas
    tarifa = producto_dict["tarifas"]["tipos_interes"][grupo_adquisicion]
    tasas = extraer_tasas(tarifa)

    # 4. Cálculo de intereses
    resultado = _calcular_intereses(tasas, bonificaciones, tarifa)
    return f"""Se ha calculado el tipo de interés final aplicando las bonificaciones acordadas.
        Por favor, indicale al usuario que se ha utilizado el grupo de adquisión:
            - Grupo de adquisición: {resultado['grupo_adquisicion']}

        Los tipos de interés calculados son:
        - Interés inicial calculado: {resultado['interes_inicial_calculado']}%
        - Interés resto calculado: {resultado['interes_resto_calculado']}%
        - Índice del resto del periodo: {resultado['indice_resto']}

        Por favor, muéstraselos al usuario. 
        Si el usuario lo solicita, se deben mostrar las promociones vigentes utilizando la herramienta 
        'consultar_promociones' o se continúa con el guardado de la muestra de interés."""


# ------------------ Helpers ------------------ #


def _validar_parametros(
    codigo_administrativo, grupo_adquisicion, bonificaciones
) -> str:
    """Función auxiliar para el cálculo de bonificaciones. Sirve para validar parámetros."""
    errores = ""
    if (
        not codigo_administrativo
        or "050" not in codigo_administrativo
        or len(codigo_administrativo) != 6
    ):
        errores += (
            "Debe indicar un código administrativo de producto válido. "
            "Debe ser un código de 6 cifras, que empieza por '050'\n"
        )
    if not grupo_adquisicion or "grupo_adquisicion_vivienda_" not in grupo_adquisicion:
        errores += (
            "Debe indicar el grupo de adquisición para el que se quiere obtener la tarifa "
            "(grupo_adquisicion_vivienda_1, grupo_adquisicion_vivienda_2, grupo_no_adquisicion_vivienda)\n"
        )
    if bonificaciones is None:
        errores += (
            "Debe indicar un valor para las bonificaciones a aplicar. "
            "Si no se han añadido bonificaciones, indicar array vacío\n"
        )
    return errores


def _obtener_producto_dict(codigo_administrativo: str) -> Optional[dict]:
    """Función auxiliar para el cálculo de bonificaciones"""
    db_session = get_manual_db_session()
    try:
        producto = (
            db_session.query(FichaProductoHipoteca)
            .filter_by(COD_ID_PROD_HIPO=codigo_administrativo)
            .first()
        )
        if producto is None:
            return None
        return json.loads(producto.DES_JSON)
    finally:
        db_session.close()


def _calcular_intereses(tasas, bonificaciones: List[Bonificacion], tarifa: str) -> dict:
    """Función auxiliar en el cálculo de bonificaciones. Permite calcular los intereses"""
    (
        interes_periodo_inicial_bonificado,
        interes_periodo_inicial_sin,
        interes_resto_bonificado,
        interes_resto_sin,
    ) = tasas

    bonificacion_total = sum(abs(b.valor) for b in bonificaciones)

    interes_inicial = max(
        interes_periodo_inicial_bonificado,
        interes_periodo_inicial_sin - bonificacion_total,
    )
    interes_resto = max(
        interes_resto_bonificado, interes_resto_sin - bonificacion_total
    )

    indice_resto = "Eur" if "EUR" in tarifa.upper() else ""

    return {
        "grupo_adquisicion": tarifa,  # cuidado: antes usabas grupo_adquisicion, ajusta según quieras
        "interes_inicial_calculado": interes_inicial,
        "interes_resto_calculado": interes_resto,
        "indice_resto": indice_resto,
    }


@tool("guardar_opinion")
async def guardar_opinion(valoracion: int, comentarios: str, id_sesion: str):
    """
    Guarda la opinión del usuario sobre Unidesk IA y su servicio de asistencia en el proceso comercial de hipotecas

    Args:
        valoracion (int): Valoración global del servicio de 0 al 10
        comentarios (str): Comentarios que quieras comunicar a los desarrolladores del sistema
        id_sesion (str): Identificador de sesión asignado en
        el primer mensaje de la conversación
    """
    try:
        tool_name = inspect.currentframe().f_code.co_name
        LogToolFunction.log_initialization(tool_name)

        # Usar el contexto distribuido actual
        distributed_context = get_current_distributed_context()
        session_metrics = distributed_context.get_session_metrics()

        session_metrics.valoracion = valoracion
        session_metrics.comentarios = comentarios

        # Guardar usando el contexto distribuido
        distributed_context.save_session_metrics()

    except Exception as e:
        # Fallback al método anterior si hay problemas
        session_metrics.valoracion = valoracion
        session_metrics.comentarios = comentarios
        session_metrics.actualizar()
        LogToolFunction.log_failure("guardar_opinion", e, None)
        SessionDAO().update_session(session_metrics)


def sumar_numeros(diccionario):
    """
    Funcion para sumar_numeros
    """
    total = 0
    for key, value in diccionario.items():
        if isinstance(value, (int, float)):  # Verifica si el valor es numérico
            total += value
    return total


# Tools definitions


@tool("calcular_gastos_tasacion", args_schema=DatosGastosTasacion)
async def calcular_gastos_tasacion(
    precio_vivienda: Optional[float] = None,
    provincia: Optional[str] = None,
    indicador_vivienda_habitual: Optional[str] = None,
    tipo_vivienda: Optional[int] = None,
    fecha_nacimiento: Optional[str] = None,
    ingresos: Optional[float] = None,
):
    """
    Calcula los gastos de tasación asociados a la financiación hipotecaria.
    """

    tool_name = inspect.currentframe().f_code.co_name
    LogToolFunction.log_initialization(tool_name)

    datos = DatosGastosTasacion(
        precio_vivienda=precio_vivienda,
        provincia=provincia,
        indicador_vivienda_habitual=indicador_vivienda_habitual,
        tipo_vivienda=tipo_vivienda,
        fecha_nacimiento=fecha_nacimiento,
        ingresos=ingresos,
    )

    errores = datos.validate_data()
    if errores:
        return {
            "error": "Faltan datos obligatorios para calcular los gastos de tasación",
            "datos_faltantes": errores,
            "mensaje_para_usuario": (
                "Para calcular los gastos de tasación necesito:\n"
                + "\n".join(f"• {error}" for error in errores)
            ),
        }

    try:
        tasacion = GastosTasacionService().call(
            precio_vivienda,
            provincia,
            indicador_vivienda_habitual,
            tipo_vivienda,
            fecha_nacimiento,
            ingresos,
        )

        return {
            "gastos_tasacion": {
                "tasacion": tasacion,
                "total": tasacion,
            },
            "mensaje_para_usuario": (
                "La tasación es un gasto asociado a la financiación hipotecaria."
            ),
        }

    except Exception as e:
        mensaje = {
            "error": f"Error al calcular los gastos de tasación: {str(e)}",
            "mensaje_para_usuario": (
                "Se ha producido un error técnico al calcular la tasación."
            ),
        }
        LogToolFunction.log_failure("calcular_gastos_tasacion", mensaje)
        return mensaje


@tool(
    "calcular_gastos_escritura_compraventa", args_schema=DatosGastosEscrituraCompraventa
)
async def calcular_gastos_escritura_compraventa(**kwargs):
    """
    Calcula los gastos de la escritura de compraventa.
    """

    tool_name = inspect.currentframe().f_code.co_name
    LogToolFunction.log_initialization(tool_name)

    datos = DatosGastosEscrituraCompraventa(**kwargs)

    errores = datos.validate_data()
    if errores:
        return {
            "error": "Faltan datos obligatorios para calcular los gastos de escritura",
            "datos_faltantes": errores,
            "mensaje_para_usuario": (
                "Para calcular los gastos de la escritura de compraventa necesito:\n"
                + "\n".join(f"• {error}" for error in errores)
            ),
        }

    try:
        gastos = GastosHipotecariosService().call(
            datos.precio_vivienda, datos.tipo_vivienda, datos.provincia
        )

        total = (
            gastos["notario"]
            + gastos["registro"]
            + gastos["honorarios"]
            + gastos["hacienda"]
        )

        return {
            "gastos_escritura_compraventa": {
                "notaria": gastos["notario"],
                "registro_propiedad": gastos["registro"],
                "gestoria": gastos["honorarios"],
                "impuestos": gastos["hacienda"],
                "total": total,
            },
            "mensaje_para_usuario": (
                "Estos son los gastos asociados exclusivamente a la escritura de compraventa."
            ),
        }

    except Exception as e:
        mensaje = {
            "error": f"Error al calcular los gastos de escritura: {str(e)}",
            "mensaje_para_usuario": (
                "Se ha producido un error técnico al calcular los gastos de escritura."
            ),
        }

        LogToolFunction.log_failure(
            "calcular_gastos_escritura_compraventa", mensaje, None
        )
        return mensaje


################ CÁLCULO DE CUOTAS #######################


def is_leap_year(year):
    """Check if a given year is a leap year."""
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)


def days_in_months_for_period(years, start_date=None):
    """
    Calculate the number of days in each month starting from the provided start date
    or the current date if no start date is provided, for the given period of years.

    Args:
    - years: The number of years for the period.
    - start_date: Optional; a datetime object representing the starting date.

    Returns:
    A dictionary with:
      - "days": An array of the number of days in each month.
      - "year_month": An array of tuples (year, month)
      corresponding to each entry in "days".
    """

    if start_date is None:
        start_date = datetime.now()

    current_year = start_date.year
    current_month = start_date.month

    # Days in each month for a non-leap year
    month_days = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

    days_array = []
    year_month_array = []

    year = current_year
    month = current_month

    for _ in range(years * 12):
        if month == 2 and is_leap_year(year):
            days = 29
        else:
            days = month_days[month - 1]

        days_array.append(days)
        year_month_array.append((year, month))

        month += 1
        if month > 12:
            month = 1
            year += 1

    return {"days": days_array, "year_month": year_month_array}


def calcular_cuota_mensual(capital, interes_anual, num_cuotas, dias_por_mes):
    """
    Función para calcular la cuota mensual de un préstamo,
    usando la fórmula de
    https://www.unicajabanco.es/es/particulares/hipotecas-y-prestamos/simulador-hipotecas

    Parámetros:
    capital (float): El capital o cantidad nominal del préstamo.
    interes_anual (float): El tipo de interés anual nominal (en porcentaje).
    num_cuotas (int): El número de cuotas a pagar.
    dias_por_mes (list): Lista con los días de devengo de cada mes.

    Retorna:
    float: La cuota mensual a pagar.
    """
    i = interes_anual / 100  # Convertimos el interés anual de porcentaje a decimal

    if len(dias_por_mes) != num_cuotas:
        raise ValueError(
            "La lista de días por mes debe tener el mismo número de elementos que el número de cuotas."
        )

    sumatoria = 0
    for s in range(1, num_cuotas + 1):
        productoria = 1
        for r in range(1, s + 1):
            pr = dias_por_mes[r - 1]
            productoria *= (1 + ((i * pr) / 365)) ** (-1)
        sumatoria += productoria

    cuota = capital / sumatoria
    return cuota


@tool("calcular_cuota_hipoteca", args_schema=DatosCuotaHipoteca)
async def calcular_cuota_hipoteca(
    tipo_hipoteca: Optional[str] = None,
    tipo_interes_inicial: Optional[float] = None,
    tipo_interes_posterior: Optional[float] = None,
    capital_prestado: Optional[float] = None,
    plazo_anos: Optional[int] = None,
    comision_apertura: Optional[float] = 0.15,
    periodo_interes_inicial: Optional[int] = 6,
    euribor_inicial: Optional[float] = 3.166,
    bonificacion: Optional[bool] = None,
) -> Dict[str, Any]:
    """
    Calcula la cuota mensual de una hipoteca (método de amortización francés) y
    devuelve también métricas clave del préstamo.

    Args:
    tipo_hipoteca (str): "fija", "mixta", o "variable".
    tipo_interes_inicial (float): Tasa de interés anual inicial (%).
    tipo_interes_posterior (float): Tasa de interés anual posterior (%).
    capital_prestado (float): Monto del préstamo (€).
    plazo_anos (int): Plazo del préstamo (años).
    comision_apertura (float): Comisión de apertura (%).
    periodo_interes_inicial (int): Periodo inicial (meses)
    euribor_inicial (float): Valor del Euribor para interés
    variable en % (3.166% por defecto).
    bonificacion (bool): Si se cumplen o requisitos de bonificación.

    Retorna:
        dict:
            - Si faltan datos o no superan validación:
              {
                "error": "...",
                "datos_faltantes": [ ... ],
                "mensaje_para_usuario": "..."
              }
            - Si todo es correcto:
                 dict: {'cuota_inicial': Cuota mensual inicial,
                        'cuota_posterior': Cuota mensual posterior,
                        'capital_pendiente': Capital pendiente tras el periodo inicial,
                        'importe_total_adeudado': importe total adeudado,
                        'intereses_totales': intereses totales pagados}.

    """
    tool_name = inspect.currentframe().f_code.co_name
    LogToolFunction.log_initialization(tool_name)

    # 1) Crear el objeto de datos para validación
    datos = DatosCuotaHipoteca(
        tipo_hipoteca=tipo_hipoteca,
        tipo_interes_inicial=tipo_interes_inicial,
        tipo_interes_posterior=tipo_interes_posterior,
        capital_prestado=capital_prestado,
        plazo_anos=plazo_anos,
        comision_apertura=comision_apertura,
        periodo_interes_inicial=periodo_interes_inicial,
        euribor_inicial=euribor_inicial,
        bonificacion=bonificacion,
    )

    # 2) Validar los datos de entrada (usando el método del modelo)
    errores = datos.validate_data()
    if errores:
        return {
            "error": "Faltan datos obligatorios o hay valores inválidos para calcular la cuota hipotecaria",
            "datos_faltantes": errores,
            "mensaje_para_usuario": (
                "Para calcular la cuota hipotecaria necesito la siguiente información y/o correcciones:\n"
                + "\n".join(f"• {e}" for e in errores)
            ),
        }

    try:
        # Cálculo del tipo de interés variable posterior en base al euribor dado.
        # El hecho de que sea bonificado o no viene implicito en el tipo de interes posterior dado (0,75 o)
        if tipo_hipoteca == "variable":
            tipo_interes_posterior = tipo_interes_posterior + euribor_inicial

        # 1. Cuota para el periodo inicial (interés fijo el primer año)
        num_cuotas_totales = plazo_anos * 12
        periodo = days_in_months_for_period(plazo_anos)
        dias_por_mes = periodo["days"]
        cuota_inicial = calcular_cuota_mensual(
            capital_prestado, tipo_interes_inicial, num_cuotas_totales, dias_por_mes
        )

        # Capital amortizado durante el periodo inicial de interés (primer año)
        capital_restante = capital_prestado
        for _ in range(periodo_interes_inicial):
            interes_mensual = (tipo_interes_inicial / 100 / 12) * capital_restante
            amortizacion = cuota_inicial - interes_mensual
            capital_restante -= amortizacion

        # 2. Cuota para el periodo posterior (interés variable después del primer año)
        cuota_posterior = calcular_cuota_mensual(
            capital_restante,
            tipo_interes_posterior,
            num_cuotas_totales - periodo_interes_inicial,
            dias_por_mes[periodo_interes_inicial:],
        )

        # 3. Calcular el importe total adeudado
        importe_total_adeudado = (
            cuota_inicial * periodo_interes_inicial
            + cuota_posterior * (num_cuotas_totales - periodo_interes_inicial)
        )

        # 4. Calcular los intereses totales pagados
        interes_total_pagado = importe_total_adeudado - capital_prestado

        # 5. Capital pendiente tras el periodo inicial
        capital_pendiente = capital_restante

        resultado = {
            "cuota_inicial": round(cuota_inicial, 2),
            "cuota_posterior": round(cuota_posterior, 2),
            "capital_pendiente": round(capital_pendiente, 2),
            "importe_total_adeudado": round(importe_total_adeudado, 2),
            "intereses_totales": round(interes_total_pagado, 2),
        }
    except Exception as e:
        resultado = {
            "error": f"Error al simular la cuota de la hipoteca: {str(e)}",
            "mensaje_para_usuario": """Se ha producido un error técnico al simular la cuota para la hipoteca. 
            Por favor, inténtalo de nuevo.""",
        }
        LogToolFunction.log_failure("calcular_cuota_hipoteca", resultado, None)
    return resultado


@tool("get_current_time")
async def get_current_time():
    """Tool para obtener la hora y fecha actual. Si tienes que calcular alguna fecha de antigüedad o edad,
    utiliza esta tool para tomar la fecha de referencia.
    """
    import datetime

    tool_name = inspect.currentframe().f_code.co_name
    LogToolFunction.log_initialization(tool_name)

    now = datetime.datetime.now()
    return now.strftime(DATETIME_FORMAT)
