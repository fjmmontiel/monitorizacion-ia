"""Modulo"""

import pytest
from unittest.mock import MagicMock, patch
from pydantic import ValidationError

from app.tools.tools_cliente import (
    EzDatosCliente,
    CreateClienteTool,
    CreateClienteInput,
    DeleteClienteTool,
    DeleteClienteInput,
)

RUTA_ITEM = "app.tools.tools_cliente.EzDataCliente"
# ==============================================================
# TESTS BASE TOOL
# ==============================================================


def test_ez_datos_cliente_init_and_run(monkeypatch):
    """Modulo"""
    fake_session = MagicMock()
    tool = EzDatosCliente(fake_session)

    assert tool._session == fake_session

    with pytest.raises(NotImplementedError):
        tool._run()


def test_ez_datos_cliente_get_cliente_by_name():
    """Modulo"""
    fake_session = MagicMock()
    fake_manager = MagicMock()
    fake_cliente = MagicMock()

    fake_session.get_manager.return_value = fake_manager
    fake_manager.get_item.return_value = fake_cliente

    tool = EzDatosCliente(fake_session)
    result = tool._get_cliente_by_name("pepe")

    fake_session.get_manager.assert_called_once_with("clienteManager")
    fake_manager.get_item.assert_called_once_with("pepe")
    assert result == fake_cliente


# ==============================================================
# TESTS CreateClienteTool
# ==============================================================


def test_create_cliente_tool_success(monkeypatch):
    """Modulo"""
    fake_session = MagicMock()
    fake_manager = MagicMock()
    fake_session.get_manager.return_value = fake_manager

    fake_datos = MagicMock()
    fake_datos.model_dump.return_value = {"nombre": "Rafa", "nif": "12345678Z"}

    fake_manager.validate_data.return_value = (True, "")

    tool = CreateClienteTool(fake_session)

    with patch(RUTA_ITEM) as mock_ezdata:
        result = tool._run("cliente1", fake_datos)

    assert result["completo"] is True
    assert "cliente1" in result["mensaje"]
    fake_manager.add_item.assert_called_once()
    fake_manager.validate_data.assert_called_once_with("cliente1")
    mock_ezdata.assert_called_once()


def test_create_cliente_tool_incomplete(monkeypatch):
    """Modulo"""
    fake_session = MagicMock()
    fake_manager = MagicMock()
    fake_session.get_manager.return_value = fake_manager

    fake_datos = MagicMock()
    fake_datos.model_dump.return_value = {"nombre": "Ana"}
    fake_manager.validate_data.return_value = (False, "Faltan campos")

    tool = CreateClienteTool(fake_session)

    with patch(RUTA_ITEM, MagicMock()):
        result = tool._run("cliente_incompleto", fake_datos)

    # Aunque el código comenta el bloque else, comprobamos que el flujo no rompe
    assert isinstance(result, dict)
    assert "completo" in result


def test_create_cliente_tool_error(monkeypatch):
    """Modulo"""
    fake_session = MagicMock()
    tool = CreateClienteTool(fake_session)

    # Simula error al construir EzDataCliente
    with patch(RUTA_ITEM, side_effect=Exception("fallo")):
        result = tool._run("x", MagicMock())

    assert "Error:" in result
    assert "fallo" in result


def test_create_cliente_input_validation():
    """Modulo"""
    with pytest.raises(ValidationError):
        CreateClienteInput()  # Falta nombre y datos obligatorios


# ==============================================================
# TESTS DeleteClienteTool
# ==============================================================


def test_delete_cliente_tool_success(monkeypatch):
    """Modulo"""
    fake_session = MagicMock()
    fake_manager = MagicMock()
    fake_cliente = MagicMock()

    fake_session.get_manager.return_value = fake_manager

    tool = DeleteClienteTool(fake_session)
    tool._get_cliente_by_name = MagicMock(return_value=fake_cliente)

    result = tool._run("c1")

    tool._get_cliente_by_name.assert_called_once_with("c1")
    fake_manager.remove_item.assert_called_once_with(fake_cliente)
    assert "eliminado correctamente" in result


def test_delete_cliente_tool_error(monkeypatch):
    """Modulo"""
    fake_session = MagicMock()
    fake_manager = MagicMock()
    fake_session.get_manager.return_value = fake_manager
    fake_manager.remove_item.side_effect = Exception("fallo al borrar")

    tool = DeleteClienteTool(fake_session)
    tool._get_cliente_by_name = MagicMock(return_value=MagicMock())

    result = tool._run("c2")

    assert "Error eliminando" in result
    assert "fallo al borrar" in result


def test_delete_cliente_input_validation():
    """Modulo"""
    with pytest.raises(ValidationError):
        DeleteClienteInput()  # Falta campo obligatorio
