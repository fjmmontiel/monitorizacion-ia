"""Tests para chat helpers."""

import pytest
import asyncio
import datetime
from decimal import Decimal
from unittest.mock import MagicMock, patch, AsyncMock

from app.services.chat_helpers import ChatHelpers, procesar_evento, procesar_tool_end

CONTENIDO_VACIO = "contenido sin metadata"
# ---------- FIXTURES Y HELPERS ----------

RUTA_CONTAR_TOKENS = "app.services.llm_service.contar_tokens"
MOCK_SESSION_ID = "session123"
MOCK_TIMESTAMP = "2025-10-23"


@pytest.fixture
def mock_chat_instance():
    """Chat instance completamente mockeada para testing."""
    chat = MagicMock()
    chat.session_id = MOCK_SESSION_ID
    chat.prompt = "hola mundo"
    chat.message_history = [
        MagicMock(content="mensaje1"),
        MagicMock(content="mensaje2"),
    ]

    # distributed context con session_manager
    mock_session = MagicMock()
    mock_session.input_tokens = 0
    mock_session.output_tokens = 0
    mock_session.cost = Decimal("0.0")
    mock_session.calcular_costes_dolares.return_value = 1.23
    mock_session.ultima_llamada_guardar_muestra_de_interes = None
    chat.distributed_context.session_manager.get_session.return_value = mock_session
    chat.distributed_context.get_session_metrics.return_value = mock_session

    # Métodos del chat
    chat.session_dao.insert_session = MagicMock()
    chat.session_dao.close = MagicMock()
    chat.log = MagicMock()
    chat.save_session = MagicMock()
    chat.get_centro_gestor_from_messages = MagicMock(return_value="001")
    chat.get_codigo_gestor_from_messages = MagicMock(return_value="G001")

    # pseudo_session setup
    mock_context = MagicMock()
    mock_context.get_llm_str.return_value = "contexto_llm_test"
    mock_context.to_json.return_value = {"context": "json"}
    mock_context.conversation_output_is_not_empty.side_effect = [True, False]
    mock_context.pop_convertation_output_element.return_value = "resultado_conversacion"
    chat.pseudo_session.get_context.return_value = mock_context

    return chat


@pytest.fixture
def mock_chunk_with_usage():
    """Mock de chunk con metadata de uso para testing."""
    chunk = MagicMock()
    chunk.content = "contenido test"
    chunk.usage_metadata = {"input_tokens": 10, "output_tokens": 20}
    chunk.response_metadata = {"model_name": "test-model"}
    return chunk


@pytest.fixture
def mock_chunk_without_usage():
    """Mock de chunk sin metadata de uso para testing."""
    chunk = MagicMock()
    chunk.content = CONTENIDO_VACIO
    chunk.usage_metadata = None
    return chunk


# ---------- TESTS ChatHelpers ----------


class TestChatHelpers:
    """Tests para la clase ChatHelpers y sus métodos estáticos."""

    def test_inicializar_sesion(self, mock_chat_instance):
        """Verifica que se inicializa la sesión correctamente."""
        with patch("app.services.llm_service.generar_identificador_sesion"), patch(
            "app.tools.tools_muestra_interes.obtener_hora_actual",
            return_value=MOCK_TIMESTAMP,
        ), patch("app.managers.session_manager.Session") as MockSession:

            MockSession.return_value = MagicMock()
            result = ChatHelpers.inicializar_sesion(mock_chat_instance)

            assert f"[ID_SESION={MOCK_SESSION_ID}]" in result
            mock_chat_instance.session_dao.insert_session.assert_called_once()

    def test_crear_mensaje_usuario(self, mock_chat_instance):
        """Verifica que se crea correctamente el mensaje del usuario con contexto."""
        with patch("datetime.datetime") as mock_datetime:
            mock_now = datetime.datetime(2025, 12, 5, 10, 30, 45)
            mock_datetime.now.return_value = mock_now

            resultado = ChatHelpers.crear_mensaje_usuario(mock_chat_instance)

            # Verificar componentes del mensaje
            assert "[PANEL DE CONTEXTO]" in resultado
            assert "contexto_llm_test" in resultado
            assert f"[ID SESION]\n{MOCK_SESSION_ID}" in resultado
            assert "[MENSAJE DEL USUARIO]\nmensaje2" in resultado
            assert "(Recuerda actualizar el panel de contexto)" in resultado

            # Verificar que se llamó get_llm_str
            mock_chat_instance.pseudo_session.get_context().get_llm_str.assert_called_once()

    def test_crear_mensaje_usuario_estructura_completa(self, mock_chat_instance):
        """Verifica la estructura completa del mensaje generado."""
        with patch("datetime.datetime") as mock_datetime:
            mock_datetime.now.return_value = datetime.datetime(2025, 12, 5, 15, 45, 30)

            resultado = ChatHelpers.crear_mensaje_usuario(mock_chat_instance)
            lineas = resultado.split("\n")

            # Verificar orden y estructura
            assert lineas[0] == "[PANEL DE CONTEXTO]"
            assert lineas[1] == "contexto_llm_test"
            assert lineas[2] == "[ID SESION]"
            assert lineas[3] == MOCK_SESSION_ID
            assert lineas[4] == "[FECHA]"


# ---------- TESTS procesar_evento ----------


class TestProcesarEvento:
    """Tests para la función procesar_evento y sus diferentes casos."""

    @pytest.mark.asyncio
    async def test_procesar_evento_on_tool_error(self, mock_chat_instance):
        """Verifica manejo de errores de herramientas."""
        evento = {"event": "on_tool_error", "data": {"error": "fail"}}
        resultado = []
        cabeceras = {}

        async for chunk in procesar_evento(mock_chat_instance, evento, [""], cabeceras):
            resultado.append(chunk)

        assert len(resultado) == 1
        assert "error" in resultado[0].lower()
        mock_chat_instance.log.assert_called_once()

    @pytest.mark.asyncio
    async def test_procesar_evento_on_chat_model_start(self, mock_chat_instance):
        """Verifica el procesamiento del inicio del modelo de chat."""
        evento = {"event": "on_chat_model_start", "data": {}}
        cabeceras = {"Authorization": "Bearer token"}
        resultado = []

        with patch(
            "app.services.chat_helpers.acheck_blocked", new_callable=AsyncMock
        ) as mock_check:
            async for chunk in procesar_evento(
                mock_chat_instance, evento, [""], cabeceras
            ):
                resultado.append(chunk)

            mock_check.assert_called_once_with(cabeceras)
            assert len(resultado) == 0

    @pytest.mark.asyncio
    async def test_procesar_evento_on_chat_model_stream_sin_metadata(
        self, mock_chat_instance, mock_chunk_without_usage
    ):
        """Verifica el procesamiento de stream sin metadata de uso."""
        evento = {
            "event": "on_chat_model_stream",
            "data": {"chunk": mock_chunk_without_usage},
        }
        log_container = ["contenido_previo"]
        cabeceras = {}
        resultado = []

        async for chunk in procesar_evento(
            mock_chat_instance, evento, log_container, cabeceras
        ):
            resultado.append(chunk)

        assert len(resultado) == 1
        assert resultado[0] == CONTENIDO_VACIO
        assert log_container[0] == "contenido_previo" + CONTENIDO_VACIO

    @pytest.mark.asyncio
    async def test_procesar_evento_on_tool_end(self, mock_chat_instance):
        """Verifica el procesamiento del final de herramientas."""
        evento = {
            "event": "on_tool_end",
            "name": "test_tool",
            "data": {"output": "resultado"},
        }
        cabeceras = {}
        resultado = []

        with patch(
            "app.services.chat_helpers.procesar_tool_end", return_value="processed"
        ) as mock_process:
            async for chunk in procesar_evento(
                mock_chat_instance, evento, [""], cabeceras
            ):
                resultado.append(chunk)

            # Verificar que se procesó la salida de conversación
            mock_chat_instance.pseudo_session.get_context().pop_convertation_output_element.assert_called_once()
            mock_process.assert_called_once()
            assert "resultado_conversacion" in resultado
            assert "processed" in resultado

    @pytest.mark.asyncio
    async def test_procesar_evento_tipo_desconocido(self, mock_chat_instance):
        """Verifica que eventos desconocidos no generan salida."""
        evento = {"event": "evento_desconocido", "data": {}}
        cabeceras = {}
        resultado = []

        async for chunk in procesar_evento(mock_chat_instance, evento, [""], cabeceras):
            resultado.append(chunk)

        assert len(resultado) == 0


# ---------- TESTS procesar_tool_end ----------


class TestProcesarToolEnd:
    """Tests para la función procesar_tool_end y sus casos específicos."""

    def test_procesar_tool_end_sin_error(self, mock_chat_instance):
        """Verifica procesamiento normal sin errores."""
        evento = {"name": "herramienta_normal", "data": {"output": "resultado exitoso"}}
        session_metrics = mock_chat_instance.distributed_context.get_session_metrics()

        resultado = procesar_tool_end(mock_chat_instance, evento, session_metrics)

        assert resultado == ""

    def test_procesar_tool_end_catalogo_productos(self, mock_chat_instance):
        """Verifica que no se loguea la salida del catálogo de productos."""
        evento = {
            "name": "obtener_catalogo_productos",
            "data": {"output": "catalogo completo"},
        }
        session_metrics = mock_chat_instance.distributed_context.get_session_metrics()

        resultado = procesar_tool_end(mock_chat_instance, evento, session_metrics)

        assert resultado == ""
        mock_chat_instance.log.assert_not_called()

    def test_procesar_tool_end_error_guardar_muestra_con_ultima_llamada(
        self, mock_chat_instance
    ):
        """Verifica manejo de error en guardar_muestra_de_interes con última llamada."""
        mock_ultima_llamada = MagicMock()
        mock_ultima_llamada.json.return_value = {"param1": "valor1", "param2": "valor2"}

        session_metrics = mock_chat_instance.distributed_context.get_session_metrics()
        session_metrics.ultima_llamada_guardar_muestra_de_interes = mock_ultima_llamada

        evento = {
            "name": "guardar_muestra_de_interes",
            "data": {"output": "ERROR: No se pudo guardar"},
        }

        resultado = procesar_tool_end(mock_chat_instance, evento, session_metrics)

        assert "<!-- Ha habido un error al guardar la muestra de interés" in resultado
        assert "-->" in resultado

    def test_procesar_tool_end_error_guardar_muestra_sin_ultima_llamada(
        self, mock_chat_instance
    ):
        """Verifica manejo de error en guardar_muestra_de_interes sin última llamada."""
        session_metrics = mock_chat_instance.distributed_context.get_session_metrics()
        session_metrics.ultima_llamada_guardar_muestra_de_interes = None

        evento = {
            "name": "guardar_muestra_de_interes",
            "data": {"output": "ERROR: fallo en base de datos"},
        }

        resultado = procesar_tool_end(mock_chat_instance, evento, session_metrics)

        assert resultado == ""

    def test_procesar_tool_end_error_guardar_muestra_excepcion_json(
        self, mock_chat_instance
    ):
        """Verifica manejo cuando json() falla en la última llamada."""
        mock_ultima_llamada = MagicMock()
        mock_ultima_llamada.json.side_effect = Exception("Error de serialización")

        session_metrics = mock_chat_instance.distributed_context.get_session_metrics()
        session_metrics.ultima_llamada_guardar_muestra_de_interes = mock_ultima_llamada

        evento = {
            "name": "guardar_muestra_de_interes",
            "data": {"output": "ERROR: datos corruptos"},
        }

        resultado = procesar_tool_end(mock_chat_instance, evento, session_metrics)

        assert resultado == ""
        mock_chat_instance.log.assert_any_call(
            "ERROR: no se ha podido escribir comentario oculto con la última llamada"
        )

    def test_procesar_tool_end_diferentes_tipos_output(self, mock_chat_instance):
        """Verifica procesamiento con diferentes tipos de output."""
        session_metrics = mock_chat_instance.distributed_context.get_session_metrics()

        test_cases = [
            {"output": None},
            {"output": ""},
            {"output": 123},
            {"output": ["lista", "de", "elementos"]},
            {},  # sin key output
        ]

        for i, data in enumerate(test_cases):
            evento = {"name": f"herramienta_{i}", "data": data}
            resultado = procesar_tool_end(mock_chat_instance, evento, session_metrics)
            assert resultado == ""


# ---------- TESTS DE INTEGRACIÓN ----------


class TestIntegracion:
    """Tests de integración para validar flujos completos."""

    @pytest.mark.asyncio
    async def test_flujo_completo_chat_model_stream(self, mock_chat_instance):
        """Verifica flujo completo de procesamiento de stream."""
        # Preparar eventos secuenciales
        evento_inicio = {"event": "on_chat_model_start", "data": {}}
        evento_stream = {
            "event": "on_chat_model_stream",
            "data": {"chunk": MagicMock(content="test", usage_metadata=None)},
        }
        evento_fin_tool = {
            "event": "on_tool_end",
            "name": "test_tool",
            "data": {"output": "done"},
        }

        cabeceras = {"user-id": "test"}
        log_container = [""]
        resultados = []

        with patch(
            "app.services.chat_helpers.acheck_blocked", new_callable=AsyncMock
        ), patch(
            "app.services.chat_helpers.procesar_tool_end", return_value="finalizado"
        ):

            # Procesar eventos
            for evento in [evento_inicio, evento_stream, evento_fin_tool]:
                async for chunk in procesar_evento(
                    mock_chat_instance, evento, log_container, cabeceras
                ):
                    resultados.append(chunk)

        assert "test" in resultados
        assert "resultado_conversacion" in resultados
        assert "finalizado" in resultados

    def test_session_metrics_actualizacion(self, mock_chat_instance):
        """Verifica que las métricas de sesión se actualicen correctamente."""
        session_metrics = mock_chat_instance.distributed_context.get_session_metrics()
        initial_tokens = session_metrics.input_tokens

        # Simular procesamiento que actualiza métricas
        chunk = MagicMock()
        chunk.usage_metadata = {"input_tokens": 5, "output_tokens": 10}
        chunk.response_metadata = {"model_name": "gpt-test"}

        # Verificar que los tokens se incrementaron
        session_metrics.input_tokens += chunk.usage_metadata["input_tokens"]
        session_metrics.output_tokens += chunk.usage_metadata["output_tokens"]

        assert session_metrics.input_tokens == initial_tokens + 5
        assert session_metrics.output_tokens == 10
