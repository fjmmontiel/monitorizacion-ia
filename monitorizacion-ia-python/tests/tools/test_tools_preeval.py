"""Modulo"""

import pytest
from unittest.mock import MagicMock, patch
from app.tools.tools_preeval import (
    EzPreevalBaseTool,
    CreatePreevalTool,
    DeletePreevalTool,
    UpdatePreevalTool,
)

ERROR_INESPERADO = "Error inesperado"
RUTA_DATA_SESSION = "app.tools.tools_preeval.DataSession"
RUTA_MANUAL_DB_SESSION = "app.tools.tools_preeval.get_manual_db_session"


def test_get_preeval_by_name():
    """Modulo"""
    mock_manager = MagicMock()
    mock_session = MagicMock()
    mock_session.get_manager.return_value = mock_manager
    tool = EzPreevalBaseTool(mock_session)
    mock_preeval = MagicMock()
    mock_manager.get_item.return_value = mock_preeval

    result = tool._get_preeval_by_name("test_name")
    mock_manager.get_item.assert_called_once_with("test_name")
    assert result == mock_preeval


def test_register_preeval():
    """Modulo"""
    mock_manager = MagicMock()
    mock_session = MagicMock()
    mock_session.get_manager.return_value = mock_manager
    tool = EzPreevalBaseTool(mock_session)
    mock_preeval = MagicMock()

    tool._register_preeval(mock_preeval)
    mock_manager.add_item.assert_called_once_with(mock_preeval)


def test_base_tool_run_raises_not_implemented():
    """Modulo"""
    mock_session = MagicMock()
    tool = EzPreevalBaseTool(mock_session)

    with pytest.raises(NotImplementedError) as excinfo:
        tool._run()

    assert "EzPreevalBaseTool no debe ejecutarse directamente." in str(excinfo.value)


# ---- Create Preeval tool ------


def test_create_preeval_tool_run_exception():
    """Modulo"""
    mock_session = MagicMock()
    mock_session.get_manager.side_effect = Exception(ERROR_INESPERADO)
    tool = CreatePreevalTool(mock_session)
    mock_datos = MagicMock()
    mock_datos.model_dump.return_value = {"campo": "valor"}
    result = tool._run(nombre="test", datos=mock_datos)
    assert "error" in result
    assert ERROR_INESPERADO in result["error"]


# ---- Update Preeval tool ------
def test_update_preeval_tool_run_exception():
    """Modulo"""
    mock_session = MagicMock()
    mock_session.get_manager.side_effect = Exception(ERROR_INESPERADO)
    tool = UpdatePreevalTool(mock_session)
    datos_dict = {"campo": "valor"}

    result = tool._run(nombre="test", datos=datos_dict)

    assert "error" in result
    assert "Error al actualizar los datos de la preevaluación" in result["error"]


# ---- Delete Preeval tool ------
def test_delete_preeval_tool_run_success():
    """Modulo"""
    mock_manager = MagicMock()
    mock_manager.remove_item.return_value = None

    mock_session = MagicMock()
    mock_session.get_manager.return_value = mock_manager

    tool = DeletePreevalTool(mock_session)
    result = tool._run(nombre="test")

    assert "eliminada correctamente" in result


def test_delete_preeval_tool_run_exception():
    """Modulo"""
    mock_session = MagicMock()
    mock_session.get_manager.side_effect = Exception(ERROR_INESPERADO)
    tool = DeletePreevalTool(mock_session)
    result = tool._run(nombre="test")

    assert "Error eliminando la preevaluación" in result
