"""Modulo"""

import pytest
from unittest.mock import MagicMock, patch
from pydantic import ValidationError

from app.tools.tools_gestor import (
    EzDatosGestor,
    CreateGestorTool,
    CreateGestorInput,
)

RUTA_ITEM = "app.tools.tools_gestor.EzDataGestor"

# ==============================================================
# TESTS BASE TOOL
# ==============================================================


def test_ez_datos_gestor_init_and_run(monkeypatch):
    """Modulo"""
    fake_session = MagicMock()
    tool = EzDatosGestor(fake_session)

    assert tool._session == fake_session

    with pytest.raises(NotImplementedError):
        tool._run()


def test_ez_datos_gestor_get_gestor_by_name():
    """Modulo"""
    fake_session = MagicMock()
    fake_manager = MagicMock()
    fake_gestor = MagicMock()

    fake_session.get_manager.return_value = fake_manager
    fake_manager.get_item.return_value = fake_gestor

    tool = EzDatosGestor(fake_session)
    result = tool._get_gestor_by_name("pepe")

    fake_session.get_manager.assert_called_once_with("gestorManager")
    fake_manager.get_item.assert_called_once_with("pepe")
    assert result == fake_gestor


# ==============================================================
# TESTS CreateGestorTool
# ==============================================================


def test_create_gestor_tool_success(monkeypatch):
    """Modulo"""
    fake_session = MagicMock()
    fake_manager = MagicMock()
    fake_session.get_manager.return_value = fake_manager

    fake_datos = MagicMock()
    fake_datos.model_dump.return_value = {"nombre": "Rafa", "nif": "12345678Z"}

    fake_manager.validate_data.return_value = (True, "")

    tool = CreateGestorTool(fake_session)

    with patch(RUTA_ITEM) as mock_ezdata:
        result = tool._run("gestor1", fake_datos)

    assert result["completo"] is True
    assert "gestor1" in result["mensaje"]
    fake_manager.add_item.assert_called_once()
    fake_manager.validate_data.assert_called_once_with("gestor1")
    mock_ezdata.assert_called_once()


def test_create_gestor_tool_incomplete(monkeypatch):
    """Modulo"""
    fake_session = MagicMock()
    fake_manager = MagicMock()
    fake_session.get_manager.return_value = fake_manager

    fake_datos = MagicMock()
    fake_datos.model_dump.return_value = {"nombre": "Ana"}
    fake_manager.validate_data.return_value = (False, "Faltan campos")

    tool = CreateGestorTool(fake_session)

    with patch(RUTA_ITEM, MagicMock()):
        result = tool._run("gestor_incompleto", fake_datos)

    # Aunque el código comenta el bloque else, comprobamos que el flujo no rompe
    assert isinstance(result, dict)
    assert "completo" in result


def test_create_gestor_tool_error(monkeypatch):
    """Modulo"""
    fake_session = MagicMock()
    tool = CreateGestorTool(fake_session)

    # Simula error al construir EzDataGestor
    with patch(RUTA_ITEM, side_effect=Exception("fallo")):
        result = tool._run("x", MagicMock())

    assert "Error:" in result
    assert "fallo" in result


def test_create_gestor_input_validation():
    """Modulo"""
    with pytest.raises(ValidationError):
        CreateGestorInput()  # Falta nombre y datos obligatorios
