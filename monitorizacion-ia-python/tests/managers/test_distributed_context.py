"""
Tests para el contexto distribuido.

Proporciona cobertura completa para las clases DistributedContext y
DistributedSessionManager, incluyendo persistencia en BD, gestión de sesiones
y reconstrucción de contexto.
"""

import pytest
import uuid
import json
from decimal import Decimal
from unittest.mock import Mock, patch, MagicMock
from sqlalchemy.orm import Session as SQLAlchemySession
from sqlalchemy.exc import SQLAlchemyError

from app.managers.distributed_context import (
    DistributedContext,
    DistributedSessionManager,
    distributed_session_manager,
)
from app.managers.items import ContextItem
from app.managers.context import ToolCall, ToolCallLog
from app.managers.session_manager import Session

# ---------- CONSTANTES ----------

MOCK_SESSION_ID = "test-session-123"
MOCK_HEADERS = {"Authorization": "Bearer fake_token"}
MOCK_ITEM_ID = "item-test-001"
MOCK_ITEM_NAME = "test_item"
MOCK_TOOL_CALL_DATA = {
    "tool_name": "test_tool",
    "arguments": {"param": "value"},
    "timestamp": "2025-12-05T10:30:00Z",
}
MOCK_DB_ITEM_DATA = {
    "id": MOCK_ITEM_ID,
    "type": "MockItem",
    "data": {"test": "data", "name": MOCK_ITEM_NAME},
}
PATH_SESSION_DAO = "app.managers.distributed_context.SessionDAO"
PATH_CONTEXT_REPOSITORY = "app.managers.distributed_context.ContextRepository"
DB_ERROR = "DB Error"


class MockContextItem(ContextItem):
    """Mock ContextItem para testing con funcionalidad completa."""

    def __init__(
        self, item_id: str = None, name: str = None, item_type: str = "MockItem"
    ):
        item_id = item_id or MOCK_ITEM_ID
        name = name or MOCK_ITEM_NAME
        super().__init__(item_id, name, item_type)
        self.data = {"test": "data", "name": name}
        self.additional_field = "test_value"

    def to_json(self):
        return json.dumps(
            {
                "id": self.get_id(),
                "name": self.name,
                "type": self.item_type,
                "data": self.data,
            }
        )

    def get_llm_str(self):
        return f"Mock item {self.name} with data {self.data}"

    def update_data(self, new_data: dict):
        """Método para actualizar datos durante testing."""
        self.data.update(new_data)


class TestDistributedContext:
    """Tests completos para DistributedContext con cobertura máxima."""

    @pytest.fixture
    def mock_repository(self):
        """Mock completo del repositorio de contexto."""
        mock_repo = Mock()
        mock_repo.load_all_context_items.return_value = []
        mock_repo.load_tool_call_log.return_value = []
        mock_repo.save_context_item.return_value = None
        mock_repo.delete_context_item.return_value = None
        mock_repo.save_tool_call_log.return_value = None
        mock_repo.clear_session_context.return_value = None
        return mock_repo

    @pytest.fixture
    def mock_session_dao(self):
        """Mock del DAO de sesiones."""
        with patch(PATH_SESSION_DAO) as mock_dao:
            mock_dao_instance = Mock()
            mock_session = Session(
                session_id=MOCK_SESSION_ID, centro="001", gestor="G001"
            )
            mock_dao_instance.get_session.return_value = mock_session
            mock_dao_instance.update_session.return_value = None
            mock_dao_instance.insert_session.return_value = None
            mock_dao.return_value = mock_dao_instance
            yield mock_dao

    @pytest.fixture
    def mock_context_items(self):
        """Fixture con items de contexto de prueba."""
        return [
            {
                "id": MOCK_ITEM_ID,
                "type": "MockItem",
                "data": {"test": "data1", "name": "item1"},
            },
            {
                "id": "item-002",
                "type": "DataCliente",
                "data": {"cliente_id": "12345", "nombre": "Juan"},
            },
        ]

    @pytest.fixture
    def mock_tool_calls(self):
        """Fixture con tool calls de prueba."""
        return [
            {
                "tool_name": "test_tool_1",
                "arguments": {"param1": "value1"},
                "timestamp": "2025-12-05T10:30:00Z",
            },
            {
                "tool_name": "test_tool_2",
                "arguments": {"param2": "value2"},
                "timestamp": "2025-12-05T10:31:00Z",
            },
        ]

    @pytest.fixture
    def distributed_context(self, mock_repository, mock_session_dao):
        """Fixture del contexto distribuido completamente mockeado."""
        with patch(PATH_CONTEXT_REPOSITORY) as mock_repo_class:
            mock_repo_class.return_value = mock_repository
            context = DistributedContext(MOCK_SESSION_ID, MOCK_HEADERS)
            context._loaded = False  # Evitar carga automática inicial
            return context

    def test_init_success(self, distributed_context):
        """Verifica inicialización correcta del contexto distribuido."""
        assert distributed_context.session_id == MOCK_SESSION_ID
        assert distributed_context.headers == MOCK_HEADERS
        assert distributed_context.repository is not None
        assert distributed_context.session_dao is not None
        assert not distributed_context._loaded

    def test_ensure_loaded_first_call(self, distributed_context):
        """Verifica que _ensure_loaded carga datos en la primera llamada."""
        with patch.object(distributed_context, "_load_from_database") as mock_load:
            distributed_context._ensure_loaded()
            mock_load.assert_called_once()
            assert distributed_context._loaded

    def test_ensure_loaded_already_loaded(self, distributed_context):
        """Verifica que _ensure_loaded no recarga si ya está cargado."""
        distributed_context._loaded = True
        with patch.object(distributed_context, "_load_from_database") as mock_load:
            distributed_context._ensure_loaded()
            mock_load.assert_not_called()

    def test_reconstruct_context_item_unknown_type(self, distributed_context):
        """Verifica manejo de tipos desconocidos en reconstrucción."""
        db_item = {"id": "unknown-001", "type": "UnknownType", "data": {"some": "data"}}

        result = distributed_context._reconstruct_context_item(db_item)
        assert result is None

    def test_reconstruct_context_item_exception(self, distributed_context):
        """Verifica manejo de excepciones en reconstrucción."""
        db_item = {
            "id": "error-001",
            "type": "DataCliente",
            "data": None,  # Datos inválidos
        }

        result = distributed_context._reconstruct_context_item(db_item)
        assert result is None

    def test_put_item_success(self, distributed_context):
        """Verifica inserción exitosa de item con persistencia en BD."""
        mock_item = MockContextItem()
        distributed_context._loaded = True

        with patch.object(distributed_context, "_ensure_loaded"), patch(
            "app.managers.context.Context._put_item"
        ) as mock_super_put:

            distributed_context._put_item(mock_item)

            distributed_context.repository.save_context_item.assert_called_once_with(
                MOCK_SESSION_ID, mock_item
            )
            mock_super_put.assert_called_once_with(mock_item)

    def test_put_item_db_exception(self, distributed_context):
        """Verifica manejo de excepción en persistencia de item."""
        mock_item = MockContextItem()
        distributed_context._loaded = True
        distributed_context.repository.save_context_item.side_effect = Exception(
            DB_ERROR
        )

        with pytest.raises(SQLAlchemyError):
            distributed_context._put_item(mock_item)

    def test_remove_item_success(self, distributed_context):
        """Verifica eliminación exitosa de item con actualización en BD."""
        mock_item = MockContextItem()
        distributed_context._loaded = True

        with patch.object(distributed_context, "_ensure_loaded"), patch(
            "app.managers.context.Context._remove_item"
        ) as mock_super_remove:

            distributed_context._remove_item(mock_item)

            mock_super_remove.assert_called_once_with(mock_item)
            distributed_context.repository.delete_context_item.assert_called_once_with(
                MOCK_SESSION_ID, mock_item.get_id()
            )

    def test_remove_item_db_exception(self, distributed_context):
        """Verifica que excepciones en eliminación de BD no interrumpan el flujo."""
        mock_item = MockContextItem()
        distributed_context._loaded = True
        distributed_context.repository.delete_context_item.side_effect = Exception(
            DB_ERROR
        )

        with patch("app.managers.context.Context._remove_item") as mock_super_remove:
            # No debe lanzar excepción
            distributed_context._remove_item(mock_item)
            mock_super_remove.assert_called_once_with(mock_item)

    def test_get_item_ensures_loaded(self, distributed_context):
        """Verifica que get_item asegura carga desde BD."""
        with patch.object(distributed_context, "_ensure_loaded") as mock_ensure, patch(
            "app.managers.context.Context.get_item"
        ) as mock_super_get:

            mock_super_get.return_value = MockContextItem()
            result = distributed_context.get_item(MOCK_ITEM_ID)

            mock_ensure.assert_called_once()
            mock_super_get.assert_called_once_with(MOCK_ITEM_ID)

    def test_get_llm_str_ensures_loaded(self, distributed_context):
        """Verifica que get_llm_str asegura carga desde BD."""
        with patch.object(distributed_context, "_ensure_loaded") as mock_ensure, patch(
            "app.managers.context.Context.get_llm_str"
        ) as mock_super:

            mock_super.return_value = "LLM context string"
            result = distributed_context.get_llm_str()

            mock_ensure.assert_called_once()
            assert result == "LLM context string"

    def test_to_json_ensures_loaded(self, distributed_context):
        """Verifica que to_json asegura carga desde BD."""
        with patch.object(distributed_context, "_ensure_loaded") as mock_ensure, patch(
            "app.managers.context.Context.to_json"
        ) as mock_super:

            mock_super.return_value = {"context": "data"}
            result = distributed_context.to_json()

            mock_ensure.assert_called_once()
            assert result == {"context": "data"}

    def test_clear_context_success(self, distributed_context):
        """Verifica limpieza completa de contexto en memoria y BD."""
        # Setup inicial
        distributed_context.items = {"test": MockContextItem()}
        distributed_context.conversation_outputs = ["output1"]

        distributed_context.clear_context()

        # Verificar limpieza en memoria
        assert len(distributed_context.items) == 0
        assert len(distributed_context.conversation_outputs) == 0
        assert isinstance(distributed_context.tool_call_log, ToolCallLog)

        # Verificar limpieza en BD
        distributed_context.repository.clear_session_context.assert_called_once_with(
            MOCK_SESSION_ID
        )

    def test_clear_context_db_exception(self, distributed_context):
        """Verifica que excepciones en limpieza de BD no interrumpan el flujo."""
        distributed_context.repository.clear_session_context.side_effect = Exception(
            DB_ERROR
        )

        # No debe lanzar excepción
        distributed_context.clear_context()
        assert len(distributed_context.items) == 0

    def test_save_session_metrics_update_existing(self, distributed_context):
        """Verifica guardado de métricas para sesión existente."""
        mock_session = Mock()
        mock_session.actualizar = Mock()
        distributed_context.session_metrics = mock_session
        distributed_context.session_dao.get_session.return_value = (
            mock_session  # Existe
        )

        distributed_context.save_session_metrics()

        mock_session.actualizar.assert_called_once()
        distributed_context.session_dao.update_session.assert_called_once_with(
            mock_session
        )
        distributed_context.session_dao.insert_session.assert_not_called()

    def test_save_session_metrics_insert_new(self, distributed_context):
        """Verifica guardado de métricas para sesión nueva."""
        mock_session = Mock()
        mock_session.actualizar = Mock()
        distributed_context.session_metrics = mock_session
        distributed_context.session_dao.get_session.return_value = None  # No existe

        distributed_context.save_session_metrics()

        mock_session.actualizar.assert_called_once()
        distributed_context.session_dao.insert_session.assert_called_once_with(
            mock_session
        )
        distributed_context.session_dao.update_session.assert_not_called()

    def test_save_session_metrics_exception(self, distributed_context):
        """Verifica manejo de excepciones en guardado de métricas."""
        mock_session = Mock()
        mock_session.actualizar.side_effect = Exception(DB_ERROR)
        distributed_context.session_metrics = mock_session

        # No debe lanzar excepción
        distributed_context.save_session_metrics()

    def test_get_session_metrics(self, distributed_context):
        """Verifica obtención de métricas de sesión."""
        mock_session = Mock()
        distributed_context.session_metrics = mock_session

        result = distributed_context.get_session_metrics()
        assert result == mock_session

    def test_refresh_from_database_success(self, distributed_context):
        """Verifica recarga forzada desde base de datos."""
        mock_db_session = Mock()
        distributed_context.session_dao.get_session.return_value = mock_db_session
        distributed_context._loaded = True

        with patch.object(distributed_context, "_ensure_loaded") as mock_ensure:
            distributed_context.refresh_from_database()

            # Debe forzar recarga
            assert not distributed_context._loaded  # Reset antes de _ensure_loaded
            mock_ensure.assert_called_once()
            assert distributed_context.session_metrics == mock_db_session

    def test_refresh_from_database_no_existing_session(self, distributed_context):
        """Verifica recarga cuando no existe sesión en BD."""
        distributed_context.session_dao.get_session.return_value = None

        with patch.object(distributed_context, "_ensure_loaded"), patch.object(
            distributed_context, "save_session_metrics"
        ) as mock_save:

            distributed_context.refresh_from_database()
            mock_save.assert_called_once()

    def test_refresh_from_database_exception(self, distributed_context):
        """Verifica manejo de excepciones en recarga desde BD."""
        distributed_context.session_dao.get_session.side_effect = Exception(DB_ERROR)

        with patch.object(distributed_context, "_ensure_loaded"):
            # No debe lanzar excepción
            distributed_context.refresh_from_database()


class TestDistributedSessionManager:
    """Tests completos para DistributedSessionManager."""

    @pytest.fixture
    def session_manager(self):
        """Fixture del gestor de sesiones distribuidas."""
        return DistributedSessionManager()

    @pytest.fixture
    def mock_all_managers(self):
        """Mock completo de todos los managers."""
        with patch("app.managers.managers.DataClienteManager") as mock_cliente, patch(
            "app.managers.managers.DataGestorManager"
        ) as mock_gestor, patch(
            "app.managers.managers.DataPreevalManager"
        ) as mock_preeval, patch(
            "app.managers.managers.DataOperacionManager"
        ) as mock_operacion, patch(
            "app.managers.managers.DataIntervinienteManager"
        ) as mock_interviniente, patch(
            "app.managers.managers.RecomendacionHipotecaManager"
        ) as mock_recomendacion, patch(
            "app.managers.managers.DataMuestraInteresManager"
        ) as mock_muestra:

            # Setup mocks
            managers = {
                "cliente": mock_cliente.return_value,
                "gestor": mock_gestor.return_value,
                "preeval": mock_preeval.return_value,
                "operacion": mock_operacion.return_value,
                "interviniente": mock_interviniente.return_value,
                "recomendacion": mock_recomendacion.return_value,
                "muestra": mock_muestra.return_value,
            }

            for manager in managers.values():
                manager.add_observer = Mock()
                manager.add_item = Mock()

            yield managers

    def test_create_context_success(self, session_manager, mock_all_managers):
        """Verifica creación exitosa de contexto distribuido."""
        with patch(
            "app.managers.distributed_context.DistributedContext"
        ) as mock_context_class:
            mock_context = Mock()
            mock_context.items = {}
            mock_context_class.return_value = mock_context

            result = session_manager.create_context(MOCK_SESSION_ID, MOCK_HEADERS)

            mock_context_class.assert_called_once_with(MOCK_SESSION_ID, MOCK_HEADERS)
            assert result == mock_context

            # Verificar que se configuraron los managers
            assert hasattr(mock_context, "managers")

    def test_setup_managers_for_context(self, session_manager, mock_all_managers):
        """Verifica configuración correcta de managers para el contexto."""
        # Crear contexto mock
        mock_context = Mock()
        mock_context.items = {
            "item1": MockContextItem("item1", "test1"),
            "item2": Mock(item_type="DataCliente"),
        }

        session_manager._setup_managers_for_context(mock_context)

        # Verificar que se crearon los managers
        assert hasattr(mock_context, "managers")
        expected_managers = [
            "clienteManager",
            "gestorManager",
            "preevalManager",
            "operacionManager",
            "intervinienteManager",
            "recomendacionHipotecaManager",
            "muestraInteresManager",
        ]

        for manager_name in expected_managers:
            assert manager_name in mock_context.managers

        # Verificar que se añadieron observers
        for manager in mock_all_managers.values():
            manager.add_observer.assert_called_with(mock_context)

    def test_setup_managers_items_mapping(self, session_manager, mock_all_managers):
        """Verifica mapeo correcto de items a sus managers correspondientes."""
        # Crear items de prueba
        mock_items = {
            "cliente1": Mock(item_type="DataCliente"),
            "gestor1": Mock(item_type="DataGestor"),
            "recom1": Mock(item_type="RecomendacionHipoteca"),
        }

        mock_context = Mock()
        mock_context.items = mock_items

        session_manager._setup_managers_for_context(mock_context)

        # Verificar que se añadieron items a managers correspondientes
        mock_all_managers["cliente"].add_item.assert_called_with(mock_items["cliente1"])
        mock_all_managers["gestor"].add_item.assert_called_with(mock_items["gestor1"])
        mock_all_managers["recomendacion"].add_item.assert_called_with(
            mock_items["recom1"]
        )

    def test_get_manager_existing_session(self, session_manager):
        """Verifica obtención de manager para sesión existente."""
        # Setup contexto existente
        mock_manager = Mock()
        mock_context = Mock()
        mock_context.managers = {"testManager": mock_manager}
        session_manager._contexts = {MOCK_SESSION_ID: mock_context}

        result = session_manager.get_manager(MOCK_SESSION_ID, "testManager")
        assert result == mock_manager

    def test_get_manager_non_existing_session(self, session_manager):
        """Verifica obtención de manager para sesión no existente."""
        session_manager._contexts = {}

        result = session_manager.get_manager(MOCK_SESSION_ID, "testManager")
        assert result is None

    def test_get_manager_non_existing_manager(self, session_manager):
        """Verifica obtención de manager no existente."""
        mock_context = Mock()
        mock_context.managers = {"otherManager": Mock()}
        session_manager._contexts = {MOCK_SESSION_ID: mock_context}

        result = session_manager.get_manager(MOCK_SESSION_ID, "nonExistentManager")
        assert result is None

    def test_remove_session_context_existing(self, session_manager):
        """Verifica eliminación de contexto de sesión existente."""
        session_manager._contexts = {MOCK_SESSION_ID: Mock(), "other-session": Mock()}

        session_manager.remove_session_context(MOCK_SESSION_ID)

        assert MOCK_SESSION_ID not in session_manager._contexts
        assert "other-session" in session_manager._contexts

    def test_remove_session_context_non_existing(self, session_manager):
        """Verifica eliminación de contexto de sesión no existente."""
        session_manager._contexts = {"other-session": Mock()}

        # No debe lanzar excepción
        session_manager.remove_session_context(MOCK_SESSION_ID)

        assert "other-session" in session_manager._contexts

    def test_distributed_session_manager_global_instance(self):
        """Verifica que existe la instancia global del gestor."""
        assert distributed_session_manager is not None
        assert isinstance(distributed_session_manager, DistributedSessionManager)


# ---------- TESTS DE INTEGRACIÓN ----------


class TestIntegracionDistributedContext:
    """Tests de integración para validar flujos completos."""

    @pytest.fixture
    def full_context_setup(self):
        """Setup completo para tests de integración."""
        with patch(PATH_CONTEXT_REPOSITORY) as mock_repo_class, patch(
            PATH_SESSION_DAO
        ) as mock_dao_class:

            # Setup repository
            mock_repo = Mock()
            mock_repo_class.return_value = mock_repo

            # Setup session DAO
            mock_dao = Mock()
            mock_session = Session(MOCK_SESSION_ID, "001", "G001")
            mock_dao.get_session.return_value = mock_session
            mock_dao_class.return_value = mock_dao

            yield {
                "repository": mock_repo,
                "session_dao": mock_dao,
                "session": mock_session,
            }

    def test_flujo_completo_crud_items(self, full_context_setup):
        """Verifica flujo completo CRUD de items en contexto distribuido."""
        context = DistributedContext(MOCK_SESSION_ID, MOCK_HEADERS)
        mock_item = MockContextItem()

        # Test: Añadir item
        context._put_item(mock_item)
        full_context_setup["repository"].save_context_item.assert_called_with(
            MOCK_SESSION_ID, mock_item
        )

        # Test: Obtener item
        context.items[mock_item.get_id()] = mock_item
        result = context.get_item(mock_item.get_id())
        assert result == mock_item

        # Test: Eliminar item
        context._remove_item(mock_item)
        full_context_setup["repository"].delete_context_item.assert_called_with(
            MOCK_SESSION_ID, mock_item.get_id()
        )

    def test_flujo_completo_session_metrics(self, full_context_setup):
        """Verifica flujo completo de gestión de métricas de sesión."""
        context = DistributedContext(MOCK_SESSION_ID, MOCK_HEADERS)

        # Test: Obtener métricas
        metrics = context.get_session_metrics()
        assert metrics == full_context_setup["session"]

        # Test: Guardar métricas
        context.save_session_metrics()
        full_context_setup["session_dao"].update_session.assert_called_once()

    def test_flujo_completo_persistencia_y_recarga(self, full_context_setup):
        """Verifica flujo completo de persistencia y recarga."""
        # Setup datos en BD
        full_context_setup["repository"].load_all_context_items.return_value = [
            {"id": "test1", "type": "MockItem", "data": {"name": "item1"}}
        ]
        full_context_setup["repository"].load_tool_call_log.return_value = [
            MOCK_TOOL_CALL_DATA
        ]

        context = DistributedContext(MOCK_SESSION_ID, MOCK_HEADERS)

        # Verificar carga inicial
        context._ensure_loaded()
        full_context_setup["repository"].load_all_context_items.assert_called_with(
            MOCK_SESSION_ID
        )
        full_context_setup["repository"].load_tool_call_log.assert_called_with(
            MOCK_SESSION_ID
        )

        # Test: Recarga forzada
        context.refresh_from_database()
        assert full_context_setup["repository"].load_all_context_items.call_count >= 2

    def test_flujo_session_manager_completo(self):
        """Verifica flujo completo del session manager."""
        with patch(
            "app.managers.distributed_context.DistributedContext"
        ) as mock_context_class, patch(
            "app.managers.managers.DataClienteManager"
        ) as mock_cliente_mgr:

            mock_context = Mock()
            mock_context.items = {}
            mock_context_class.return_value = mock_context

            manager = DistributedSessionManager()

            # Test: Crear contexto
            context = manager.create_context(MOCK_SESSION_ID, MOCK_HEADERS)
            assert context == mock_context

            # Test: Configurar managers
            assert hasattr(mock_context, "managers")

            # Test: Eliminar sesión
            manager._contexts = {MOCK_SESSION_ID: mock_context}
            manager.remove_session_context(MOCK_SESSION_ID)
            assert MOCK_SESSION_ID not in manager._contexts


# ---------- TESTS DE CASOS EDGE ----------


class TestEdgeCases:
    """Tests para casos edge y situaciones límite."""

    def test_context_with_none_session_id(self):
        """Verifica comportamiento con session_id None."""
        with patch(PATH_CONTEXT_REPOSITORY), patch(PATH_SESSION_DAO):

            context = DistributedContext(None, MOCK_HEADERS)
            assert context.session_id is None

    def test_context_with_empty_headers(self):
        """Verifica comportamiento con headers vacíos."""
        with patch(PATH_CONTEXT_REPOSITORY), patch(PATH_SESSION_DAO):

            context = DistributedContext(MOCK_SESSION_ID, {})
            assert context.headers == {}

    def test_massive_items_handling(self):
        """Verifica manejo de gran cantidad de items."""
        with patch(PATH_CONTEXT_REPOSITORY) as mock_repo_class, patch(PATH_SESSION_DAO):

            mock_repo = Mock()
            mock_repo.load_all_context_items.return_value = [
                {"id": f"item-{i}", "type": "MockItem", "data": {"index": i}}
                for i in range(1000)  # 1000 items
            ]
            mock_repo.load_tool_call_log.return_value = []
            mock_repo_class.return_value = mock_repo

            context = DistributedContext(MOCK_SESSION_ID, MOCK_HEADERS)
            context._load_from_database()

            # Verificar que maneja correctamente gran cantidad de items
            assert len(mock_repo.load_all_context_items.return_value) == 1000

    def test_concurrent_access_simulation(self):
        """Simula acceso concurrente al contexto distribuido."""
        with patch(PATH_CONTEXT_REPOSITORY) as mock_repo_class, patch(PATH_SESSION_DAO):

            mock_repo = Mock()
            mock_repo_class.return_value = mock_repo

            # Simular múltiples contextos para la misma sesión
            context1 = DistributedContext(MOCK_SESSION_ID, MOCK_HEADERS)
            context2 = DistributedContext(MOCK_SESSION_ID, MOCK_HEADERS)

            assert context1.session_id == context2.session_id
            assert context1 != context2  # Diferentes instancias
