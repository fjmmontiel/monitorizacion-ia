"""Modulo"""

import pytest
from unittest.mock import MagicMock, patch
from app.tools.tools_operacion import (
    EzOperacionBaseTool,
    CreateOperacionTool,
    UpdateOperacionTool,
    DeleteOperacionTool,
)

ERROR_INESPERADO = "Error inesperado"
RUTA_MANUAL_DB_SESSION = "app.tools.tools_operacion.get_manual_db_session"


def test_get_operacion_by_name():
    """Modulo"""
    mock_manager = MagicMock()
    mock_session = MagicMock()
    mock_session.get_manager.return_value = mock_manager
    tool = EzOperacionBaseTool(mock_session)
    mock_operacion = MagicMock()
    mock_manager.get_item.return_value = mock_operacion

    result = tool._get_operacion_by_name("test_name")
    mock_manager.get_item.assert_called_once_with("test_name")
    assert result == mock_operacion


def test_register_operacion():
    """Modulo"""
    mock_manager = MagicMock()
    mock_session = MagicMock()
    mock_session.get_manager.return_value = mock_manager
    tool = EzOperacionBaseTool(mock_session)
    mock_operacion = MagicMock()

    tool._register_operacion(mock_operacion)
    mock_manager.add_item.assert_called_once_with(mock_operacion)


def test_base_tool_run_raises_not_implemented():
    """Modulo"""
    mock_session = MagicMock()
    tool = EzOperacionBaseTool(mock_session)

    with pytest.raises(NotImplementedError) as excinfo:
        tool._run()

    assert "EzOperacionBaseTool no debe ejecutarse directamente." in str(excinfo.value)


# --- UpdateOperacionTool ---
def test_update_operacion_tool_run_success():
    """Modulo"""
    mock_manager = MagicMock()
    mock_manager.update_values.return_value = None
    mock_session = MagicMock()
    mock_session.get_manager.return_value = mock_manager

    tool = UpdateOperacionTool(mock_session)
    datos_dict = {"campo": "valor"}

    # Ajuste: como _run devuelve string con keys en tu código
    result = tool._run(
        nombre="test",
        datos=MagicMock(model_dump=lambda: datos_dict),
    )

    # Se espera que no haya 'error' en el resultado
    assert "error" not in result


def test_update_operacion_tool_run_exception():
    """Modulo"""
    mock_session = MagicMock()
    mock_session.get_manager.side_effect = Exception(ERROR_INESPERADO)
    tool = UpdateOperacionTool(mock_session)
    datos_dict = {"campo": "valor"}

    result = tool._run(nombre="test", datos=datos_dict)

    assert "error" in result
    assert "Error al actualizar" in result["error"]


# --- DeleteOperacionTool ---
def test_delete_operacion_tool_run_success():
    """Modulo"""
    mock_manager = MagicMock()
    mock_manager.remove_item.return_value = None
    mock_operacion = MagicMock()
    mock_manager.get_item.return_value = mock_operacion
    mock_session = MagicMock()
    mock_session.get_manager.return_value = mock_manager

    tool = DeleteOperacionTool(mock_session)
    result = tool._run(nombre="test")

    assert "eliminada correctamente" in str(result)


def test_delete_operacion_tool_run_exception():
    """Modulo"""
    mock_session = MagicMock()
    mock_session.get_manager.side_effect = Exception(ERROR_INESPERADO)
    tool = DeleteOperacionTool(mock_session)
    result = tool._run(nombre="test")

    assert "Error eliminando la operación" in str(result)
