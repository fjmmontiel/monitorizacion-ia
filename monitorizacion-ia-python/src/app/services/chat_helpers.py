"""
Utilidades de ayuda para el servicio de chat.

Proporciona métodos auxiliares para gestionar sesiones, contabilizar tokens,
procesar eventos de stream y manejar la lógica de conversación del chatbot
de hipotecas.
"""

from decimal import Decimal
from qgdiag_lib_arquitectura import CustomLogger
from app.managers.session_manager import Session
from qgdiag_lib_arquitectura.utilities.ai_core.control_gastos import (
    acheck_blocked,
    aget_cost_data,
    log_costs,
)
import datetime
from app.tools.tools_muestra_interes import obtener_hora_actual

logger = CustomLogger("Helpers para el chat.")


class ChatHelpers:
    """Helper methods para la función chat"""

    @staticmethod
    def inicializar_sesion(chat_instance):
        """Inicializa la sesión si es la primera interacción"""

        centro = chat_instance.get_centro_gestor_from_messages()
        gestor = chat_instance.get_codigo_gestor_from_messages()

        session = Session(
            session_id=chat_instance.session_id, centro=centro, gestor=gestor
        )

        session.iniciar_sesion()
        session.actualizar_tiempos_sesion()

        chat_instance.distributed_context.session_metrics = session
        chat_instance.session_dao.insert_session(session)

        return f"[ID_SESION={chat_instance.session_id}][TIMESTAMP={obtener_hora_actual()}]\n\n"

    @staticmethod
    def crear_mensaje_usuario(chat_instance):
        """Crea el mensaje del usuario con contexto"""
        context_llm_str = chat_instance.pseudo_session.get_context().get_llm_str()

        now = datetime.datetime.now()

        return (
            f"[PANEL DE CONTEXTO]\n{context_llm_str}\n"
            f"[ID SESION]\n{chat_instance.session_id}\n"
            f"[FECHA]\n{now.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"[MENSAJE DEL USUARIO]\n{chat_instance.message_history[-1].content}\n"
            "(Recuerda actualizar el panel de contexto)\n"
        )


async def procesar_evento(chat_instance, event, log_content_container, headers):
    """Procesa un evento del stream del agente"""
    kind = event["event"]

    session_metrics = chat_instance.distributed_context.get_session_metrics()

    if kind == "on_chat_model_start":
        await acheck_blocked(headers)

    elif kind == "on_chat_model_stream":
        chunk = event["data"]["chunk"]

        if getattr(chunk, "usage_metadata", None):
            cost_data = await aget_cost_data(chunk.response_metadata["model_name"])
            log_costs(
                tokens_input=chunk.usage_metadata["input_tokens"],
                tokens_output=chunk.usage_metadata["output_tokens"],
                cost_data=cost_data,
            )
            session_metrics.input_tokens += chunk.usage_metadata["input_tokens"]
            session_metrics.output_tokens += chunk.usage_metadata["output_tokens"]
            session_metrics.cost += (
                cost_data["coste_modelo_input"] + cost_data["coste_modelo_output"]
            )

        else:
            content = chunk.content
            if content:
                log_content_container[0] += content
                yield content

    elif kind == "on_tool_end":
        while (
            chat_instance.pseudo_session.get_context().conversation_output_is_not_empty()
        ):
            yield chat_instance.pseudo_session.get_context().pop_convertation_output_element()
        yield procesar_tool_end(chat_instance, event, session_metrics)

    elif kind == "on_tool_error":
        chat_instance.log(f"Tool error: {event}")
        yield "Se ha producido un error inesperado"


def procesar_tool_end(chat_instance, event, session_metrics):
    """Procesa eventos de tool end"""

    tool_output = event["data"].get("output", "")

    result = ""

    # Manejo de error en guardar_muestra_de_interes
    if (
        event["name"] == "guardar_muestra_de_interes"
        and "error" in str(tool_output).lower()
    ):
        ultima_llamada = session_metrics.ultima_llamada_guardar_muestra_de_interes
        if ultima_llamada:
            try:
                result = f"""<!-- Ha habido un error al guardar la muestra de interés. Parametros que hay que revisar:
                {ultima_llamada.json()} -->"""
            except Exception:
                chat_instance.log(
                    "ERROR: no se ha podido escribir comentario oculto con la última llamada"
                )

    return result
