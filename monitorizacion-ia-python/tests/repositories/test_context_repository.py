"""Tests del repositorio de contexto.

Este módulo verifica el comportamiento de `ContextRepository` incluyendo:
- Carga de todos los items de contexto.
- Guardado de items de contexto (nuevo y actualización).
- Carga de un item específico.
- Limpieza del contexto de sesión.
- Carga del log de llamadas a herramientas.
- Borrado lógico de un item.
- Guardado de llamadas a herramientas.
"""

import pytest
from unittest.mock import MagicMock, patch
import json
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
from app.repositories.context_repository import ContextRepository

MANUAL_DB_SESSION = "app.repositories.context_repository.get_manual_db_session"


# ==== FIXTURES ====
@pytest.fixture
def repo():
    """Instancia de `ContextRepository` para las pruebas."""
    return ContextRepository()


@pytest.fixture
def fake_item():
    """Item simulado con estructura mínima para guardado."""
    item = MagicMock()
    item.get_id.return_value = "item1"
    item.item_type = "test_type"
    item.to_json.return_value = json.dumps({"a": 1})
    return item


@pytest.fixture
def tool_call_items():
    """Lista de tool calls simulados con JSON válido."""
    return [
        MagicMock(DES_JSON=json.dumps({"tool": "search", "args": {"q": "pytest"}})),
        MagicMock(DES_JSON=json.dumps({"tool": "calc", "args": {"expr": "2+2"}})),
    ]


# ==== TEST load_all_context_items ====
def test_load_all_context_items_ok(repo):
    """Carga varios items correctamente."""
    mock_items = [
        MagicMock(
            DES_NOMBRE_DATO="id1",
            DES_TIPO_DATO="tipo1",
            DES_JSON=json.dumps({"v": 1}),
            AUD_TIM=datetime(2024, 1, 1),
        ),
        MagicMock(
            DES_NOMBRE_DATO="id2",
            DES_TIPO_DATO="tipo2",
            DES_JSON=json.dumps({"v": 2}),
            AUD_TIM=datetime(2024, 1, 2),
        ),
    ]

    with patch(MANUAL_DB_SESSION) as mock_get_session:
        fake_session = MagicMock()
        fake_session.query.return_value.filter.return_value.order_by.return_value.all.return_value = (
            mock_items
        )
        mock_get_session.return_value = fake_session

        result = repo.load_all_context_items("sess1")
        assert len(result) == 2
        assert result[0]["data"]["v"] == 1


def test_load_all_context_items_error(repo):
    """Error al cargar items."""
    with patch(MANUAL_DB_SESSION) as mock_get_session:
        fake_session = MagicMock()
        fake_session.query.side_effect = SQLAlchemyError("DB fail")
        mock_get_session.return_value = fake_session

        with pytest.raises(SQLAlchemyError, match="Error cargando context items"):
            repo.load_all_context_items("sess1")


# ==== TEST save_context_item ====
class TestSaveContextItem:
    """Pruebas para `save_context_item`."""

    def test_crea_nuevo_item(self, repo, fake_item):
        """Crea un item nuevo si no existe previamente."""
        with patch(MANUAL_DB_SESSION) as mock_get_session:
            fake_session = MagicMock()
            fake_session.query.return_value.filter.return_value.first.return_value = (
                None
            )
            mock_get_session.return_value = fake_session

            result = repo.save_context_item("sess1", fake_item)
            assert result is True
            fake_session.add.assert_called_once()
            fake_session.commit.assert_called_once()
            fake_session.close.assert_called_once()

    def test_actualiza_item_existente(self, repo, fake_item):
        """Actualiza un item existente en la base de datos."""
        existing_item = MagicMock()
        with patch(MANUAL_DB_SESSION) as mock_get_session:
            fake_session = MagicMock()
            fake_session.query.return_value.filter.return_value.first.return_value = (
                existing_item
            )
            mock_get_session.return_value = fake_session

            result = repo.save_context_item("sess1", fake_item)
            assert result is True
            fake_session.add.assert_not_called()  # No debe añadir, solo actualizar
            assert existing_item.DES_TIPO_DATO == fake_item.item_type
            assert existing_item.DES_JSON == fake_item.to_json()
            fake_session.commit.assert_called_once()
            fake_session.close.assert_called_once()

    def test_error_guardando_item(self, repo, fake_item):
        """Propaga error y hace rollback si falla la operación."""
        with patch(MANUAL_DB_SESSION) as mock_get_session:
            fake_session = MagicMock()
            fake_session.query.side_effect = SQLAlchemyError("DB crash")
            mock_get_session.return_value = fake_session

            with pytest.raises(SQLAlchemyError, match="Error guardando context item"):
                repo.save_context_item("sess1", fake_item)
            fake_session.rollback.assert_called_once()
            fake_session.close.assert_called_once()


# ==== TEST load_context_item ====
def test_load_context_item_ok(repo):
    """Cargar un item específico correctamente."""
    mock_item = MagicMock(
        COD_ID_DATO_UNIQUE="item1",
        DES_TIPO_DATO="tipo1",
        DES_JSON=json.dumps({"v": 1}),
        AUD_TIM=datetime(2024, 1, 1),
    )

    with patch(MANUAL_DB_SESSION) as mock_get_session:
        fake_session = MagicMock()
        fake_session.query.return_value.filter.return_value.first.return_value = (
            mock_item
        )
        mock_get_session.return_value = fake_session

        result = repo.load_context_item("sess1", "item1")
        assert result["id"] == "item1"
        assert result["data"]["v"] == 1


def test_load_context_item_error(repo):
    """Error al cargar un item."""
    with patch(MANUAL_DB_SESSION) as mock_get_session:
        fake_session = MagicMock()
        fake_session.query.side_effect = SQLAlchemyError("crash")
        mock_get_session.return_value = fake_session

        with pytest.raises(SQLAlchemyError, match="Error cargando context item"):
            repo.load_context_item("sess1", "item1")


# ==== TEST clear_session_context ====
def test_clear_session_context_ok(repo):
    """Marca los items como inválidos."""
    items = [MagicMock(), MagicMock()]

    with patch(MANUAL_DB_SESSION) as mock_get_session:
        fake_session = MagicMock()
        fake_session.query.return_value.filter.return_value.all.return_value = items
        mock_get_session.return_value = fake_session

        result = repo.clear_session_context("sess1")
        assert result is True
        for it in items:
            assert it.IND_DATO_VALIDO is False
        fake_session.commit.assert_called_once()


def test_clear_session_context_error(repo):
    """Error al limpiar contexto."""
    with patch(MANUAL_DB_SESSION) as mock_get_session:
        fake_session = MagicMock()
        fake_session.query.side_effect = SQLAlchemyError("DB down")
        mock_get_session.return_value = fake_session

        with pytest.raises(SQLAlchemyError, match="Error limpiando contexto de sesión"):
            repo.clear_session_context("sess1")
        fake_session.rollback.assert_called_once()


# ==== TEST load_tool_call_log ====
class TestLoadToolCallLog:
    """Pruebas para `load_tool_call_log`."""

    def test_ok(self, repo, tool_call_items):
        """Devuelve lista parseada desde JSON."""
        with patch(MANUAL_DB_SESSION) as mock_get_session:
            fake_session = MagicMock()
            fake_session.query.return_value.filter.return_value.order_by.return_value.all.return_value = (
                tool_call_items
            )
            mock_get_session.return_value = fake_session

            result = repo.load_tool_call_log("sess1")
            assert isinstance(result, list) and len(result) == 2
            assert result[0]["tool"] == "search"
            assert result[1]["args"]["expr"] == "2+2"
            fake_session.close.assert_called_once()

    def test_vacio(self, repo):
        """Devuelve lista vacía si no hay tool calls."""
        with patch(MANUAL_DB_SESSION) as mock_get_session:
            fake_session = MagicMock()
            fake_session.query.return_value.filter.return_value.order_by.return_value.all.return_value = (
                []
            )
            mock_get_session.return_value = fake_session

            result = repo.load_tool_call_log("sess1")
            assert result == []
            fake_session.close.assert_called_once()

    def test_error(self, repo):
        """Propaga error con mensaje contextual."""
        with patch(MANUAL_DB_SESSION) as mock_get_session:
            fake_session = MagicMock()
            fake_session.query.side_effect = SQLAlchemyError("boom")
            mock_get_session.return_value = fake_session

            with pytest.raises(
                SQLAlchemyError, match="Error cargando tool call log para sesión"
            ):
                repo.load_tool_call_log("sess1")
            fake_session.close.assert_called_once()


# ==== TEST delete_context_item ====
class TestDeleteContextItem:
    """Pruebas para `delete_context_item`."""

    def test_ok(self, repo):
        """Borra el item correctamente."""
        mock_item = MagicMock()
        with patch(MANUAL_DB_SESSION) as mock_get_session:
            fake_session = MagicMock()
            fake_session.query.return_value.filter.return_value.first.return_value = (
                mock_item
            )
            mock_get_session.return_value = fake_session

            result = repo.delete_context_item("sess1", "item1")
            assert result is True
            fake_session.delete.assert_called_once_with(mock_item)
            fake_session.commit.assert_called_once()
            fake_session.close.assert_called_once()

    def test_no_item(self, repo):
        """Devuelve False si no existe el item."""
        with patch(MANUAL_DB_SESSION) as mock_get_session:
            fake_session = MagicMock()
            fake_session.query.return_value.filter.return_value.first.return_value = (
                None
            )
            mock_get_session.return_value = fake_session

            result = repo.delete_context_item("sess1", "itemX")
            assert result is False
            fake_session.delete.assert_not_called()
            fake_session.commit.assert_not_called()
            fake_session.close.assert_called_once()

    def test_error(self, repo):
        """Propaga error y hace rollback."""
        with patch(MANUAL_DB_SESSION) as mock_get_session:
            fake_session = MagicMock()
            fake_session.query.side_effect = SQLAlchemyError("fail")
            mock_get_session.return_value = fake_session

            with pytest.raises(SQLAlchemyError, match="Error borrando context item"):
                repo.delete_context_item("sess1", "item1")
            fake_session.rollback.assert_called_once()
            fake_session.close.assert_called_once()


# ==== TEST save_tool_call_log ====
class TestSaveToolCallLog:
    """Pruebas para `save_tool_call_log`."""

    def test_ok(self, repo):
        """Guarda la llamada correctamente."""
        fake_tool_call = MagicMock()
        fake_tool_call.json.return_value = json.dumps(
            {"tool": "search", "args": {"q": "pytest"}}
        )

        with patch(MANUAL_DB_SESSION) as mock_get_session:
            fake_session = MagicMock()
            mock_get_session.return_value = fake_session

            result = repo.save_tool_call_log("sess1", fake_tool_call)
            assert result is True
            fake_session.add.assert_called_once()
            fake_session.commit.assert_called_once()
            fake_session.close.assert_called_once()

    def test_error(self, repo):
        """Propaga error y hace rollback."""
        fake_tool_call = MagicMock()
        fake_tool_call.json.return_value = json.dumps({"tool": "search"})

        with patch(MANUAL_DB_SESSION) as mock_get_session:
            fake_session = MagicMock()
            fake_session.add.side_effect = SQLAlchemyError("insert fail")
            mock_get_session.return_value = fake_session

            with pytest.raises(SQLAlchemyError, match="Error guardando tool call"):
                repo.save_tool_call_log("sess1", fake_tool_call)
            fake_session.rollback.assert_called_once()
            fake_session.close.assert_called_once()
