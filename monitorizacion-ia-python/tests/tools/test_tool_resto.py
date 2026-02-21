"""Modulo"""

import pytest
from unittest.mock import MagicMock, patch
from pydantic import ValidationError

from app.tools.tools_resto import (
    EzVerificarDNI,
    VerificarDniTool,
    VerificarDniInput,
    EzConsultarConsentimiento,
    ConsultarConsentimientoTool,
    ConsultarConsentimientoInput,
    EzLogOperacional,
    LogOperacionalTool,
    LogOperacionalInput,
)


# ==============================================================
# TESTS COMUNES PARA CLASES BASE
# ==============================================================


@pytest.mark.parametrize(
    "cls",
    [EzVerificarDNI, EzConsultarConsentimiento, EzLogOperacional],
)
def test_base_tool_init_and_run_raises(cls):
    """Verifica que las clases base inicializan correctamente y _run lanza NotImplementedError"""
    fake_session = MagicMock()
    tool = cls(fake_session)
    assert tool._session == fake_session
    with pytest.raises(NotImplementedError):
        tool._run()


# ==============================================================
# TESTS VerificarDniTool
# ==============================================================


def test_verificar_dni_tool_success(monkeypatch):
    """Modulo"""
    fake_session = MagicMock()
    tool = VerificarDniTool(fake_session)

    mock_doc = MagicMock()
    mock_doc.verificar.return_value = {"valido": True}

    with patch("app.tools.tools_resto.DocumentoIdentidad", return_value=mock_doc):
        result = tool._run("12345678Z")

    assert result == {"valido": True}
    mock_doc.verificar.assert_called_once()


def test_verificar_dni_tool_error(monkeypatch):
    """Modulo"""
    fake_session = MagicMock()
    tool = VerificarDniTool(fake_session)

    with patch(
        "app.tools.tools_resto.DocumentoIdentidad",
        side_effect=ValueError("DNI inválido"),
    ):
        result = tool._run("BAD_DNI")

    assert "aviso_agente" in result


def test_verificar_dni_input_validation():
    """Modulo"""
    with pytest.raises(ValidationError):
        VerificarDniInput()  # Falta el campo obligatorio


# ==============================================================
# TESTS ConsultarConsentimientoTool
# ==============================================================


def test_consultar_consentimiento_tool_success(monkeypatch):
    """Modulo"""
    fake_datos = MagicMock()
    fake_service = MagicMock()
    fake_service.call.return_value = {"consentimiento": "aceptado"}

    with patch(
        "app.tools.tools_resto.ConsultaConsentimientoService",
        return_value=fake_service,
    ):
        tool = ConsultarConsentimientoTool(MagicMock())
        result = tool._run(fake_datos)

    assert result == {"consentimiento": "aceptado"}
    fake_service.call.assert_called_once_with(fake_datos)


def test_consultar_consentimiento_tool_error(monkeypatch):
    """Modulo"""
    fake_datos = MagicMock()
    with patch(
        "app.tools.tools_resto.ConsultaConsentimientoService",
        side_effect=Exception("Fallo"),
    ):
        tool = ConsultarConsentimientoTool(MagicMock())
        result = tool._run(fake_datos)

    assert "error" in result
    assert "Fallo" in result["error"]


def test_consultar_consentimiento_input_validation():
    """Modulo"""
    with pytest.raises(ValidationError):
        ConsultarConsentimientoInput()  # Falta el campo obligatorio


# ==============================================================
# TESTS LogOperacionalTool
# ==============================================================


def test_log_operacional_tool_success(monkeypatch):
    """Modulo"""
    fake_datos = MagicMock()
    fake_service = MagicMock()
    fake_service.call.return_value = {"ok": True}

    with patch(
        "app.tools.tools_resto.LogOperacionalService", return_value=fake_service
    ):
        tool = LogOperacionalTool(MagicMock())
        result = tool._run(fake_datos)

    assert result == {"ok": True}
    fake_service.call.assert_called_once_with(fake_datos)


def test_log_operacional_tool_error(monkeypatch):
    """Modulo"""
    fake_datos = MagicMock()
    with patch(
        "app.tools.tools_resto.LogOperacionalService",
        side_effect=Exception("Error al registrar"),
    ):
        tool = LogOperacionalTool(MagicMock())
        result = tool._run(fake_datos)

    assert "error" in result
    assert "Error al registrar" in result["error"]


def test_log_operacional_input_validation():
    """Modulo"""
    with pytest.raises(ValidationError):
        LogOperacionalInput()  # Falta el campo obligatorio
