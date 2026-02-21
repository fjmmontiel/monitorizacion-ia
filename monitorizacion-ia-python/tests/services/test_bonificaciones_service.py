"""Tests para el servicio de consulta de bonificaciones (adaptados al nuevo comportamiento)."""

import pytest
from unittest.mock import patch, MagicMock
from app.services.bonificaciones_service import BonificacionesService


# ==== FIXTURES ====
FAKE_PATH = "https://fake/api"
FALLO_API = "fallo api"
PATH_SERVICES_CONFIG = "app.services.bonificaciones_service.UnicajaServicesConfig"


@pytest.fixture
def mock_config(monkeypatch):
    """Mock de UnicajaServicesConfig"""
    cfg = MagicMock()
    cfg.token_jwt = "https://fake/token"
    cfg.api_bonificaciones = FAKE_PATH
    cfg.cookie = "cookie"
    cfg.connection = "keep-alive"
    cfg.channel_token = "ch1"
    cfg.token_fijo = "tok123"
    monkeypatch.setattr(
        PATH_SERVICES_CONFIG,
        lambda: cfg,
    )
    return cfg


@pytest.fixture
def headers(mock_config):
    """Headers simulados"""
    return {
        "Connection": mock_config.connection,
        "Cookie": mock_config.cookie,
        "Channel": mock_config.channel_token,
        "Token": mock_config.token_fijo,
    }


# === Fixtures auxiliares ===
@pytest.fixture
def headers():
    """Función para mockear los headers"""
    return {"Authorization": "Bearer fake-token"}


@pytest.fixture(autouse=True)
def mock_config(monkeypatch):
    """mock_config"""

    class FakeConfig:
        """FakeConfig"""

        api_bonificaciones = FAKE_PATH

    monkeypatch.setattr(
        PATH_SERVICES_CONFIG,
        lambda: FakeConfig(),
    )
    return True


@patch("app.services.bonificaciones_service.requests.post")
def test_consulta_bonificaciones_ok_devuelve_json_en_2xx(mock_post, headers):
    """
    Con la nueva lógica:
    - Si status es 2xx, devuelve response.json() (sin 'error').
    """
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {"resultado": "ok"}

    with patch(PATH_SERVICES_CONFIG) as mock_cfg:
        mock_cfg.return_value.api_bonificaciones = FAKE_PATH
        service = BonificacionesService(headers=headers)
        body = {"id": 1}
        res = service._consulta_bonificaciones(body)

    mock_post.assert_called_once_with(FAKE_PATH, headers=headers, json=body)
    assert isinstance(res, dict)
    assert res == {"resultado": "ok"}
    assert "error" not in res


@patch("app.services.bonificaciones_service.requests.post")
def test_consulta_bonificaciones_error_devuelve_error_dict_en_no_2xx(
    mock_post, headers
):
    """
    Con la nueva lógica:
    - Si status != 2xx, devuelve dict con 'error' incluyendo código y body.
    """
    mock_post.return_value.status_code = 500
    mock_post.return_value.json.return_value = {"detalle": FALLO_API}

    with patch(PATH_SERVICES_CONFIG) as mock_cfg:
        mock_cfg.return_value.api_bonificaciones = FAKE_PATH
        service = BonificacionesService(headers=headers)
        res = service._consulta_bonificaciones({"x": 1})

    assert isinstance(res, dict)
    assert "error" in res
    assert "500" in res["error"]
    assert FALLO_API in res["error"]  # el detalle del body aparece en el mensaje


@patch("app.services.bonificaciones_service.requests.post")
def test_call_ok_con_2xx_devuelve_json(mock_post, headers):
    """
    Dado el comportamiento actual de _consulta_bonificaciones:
    - Para 2xx, devuelve el JSON de éxito y call lo propaga tal cual.
    """
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {"resultado": "ok"}

    with patch(PATH_SERVICES_CONFIG) as mock_cfg:
        mock_cfg.return_value.api_bonificaciones = FAKE_PATH
        service = BonificacionesService(headers=headers)
        data = {"id": 123}
        result = service.call(data)

    assert isinstance(result, dict)
    assert result == {"resultado": "ok"}


@patch("app.services.bonificaciones_service.requests.post")
def test_call_exception(mock_post, mock_config, headers):
    """
    Debe devolver un dict con 'error' si requests.post lanza una excepción
    (call captura la excepción y devuelve {"error": str(e)}).
    """
    mock_post.side_effect = Exception(FALLO_API)
    service = BonificacionesService(headers=headers)
    data = {"id": 456}
    result = service.call(data)
    assert "error" in result and FALLO_API in result["error"]
