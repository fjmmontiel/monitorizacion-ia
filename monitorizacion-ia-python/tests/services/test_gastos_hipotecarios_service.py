"""Tests para el servicio de gastos de tasación."""

import pytest
from unittest.mock import patch, MagicMock
from requests.exceptions import HTTPError

from app.services.gastos_hipotecarios_service import GastosHipotecariosService

REQUEST_POST = "app.services.gastos_hipotecarios_service.requests.post"
FALLO_API = "fallo api"


@pytest.fixture
def service():
    """Instancia del servicio con configuración parcheada."""
    with patch(
        "app.services.gastos_hipotecarios_service.UnicajaServicesConfig"
    ) as mock_config:
        mock_instance = mock_config.return_value
        mock_instance.client_id = "fake_id"
        mock_instance.client_secret = "fake_secret"
        mock_instance.url_token_oauth2 = "https://fake.token.url"
        mock_instance.api_gastos_hipotecarios = "https://fake.api.url"
        yield GastosHipotecariosService()


def test_get_oauth_token_success(service):
    """Prueba que se obtiene token correctamente."""
    fake_response = MagicMock()
    fake_response.json.return_value = {"access_token": "fake_token"}
    fake_response.raise_for_status.return_value = None

    with patch(
        REQUEST_POST,
        return_value=fake_response,
    ) as mock_post:
        token = service._get_oauth_token("id", "secret")
        assert token == "fake_token"
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        assert kwargs["data"]["client_id"] == "id"
        assert kwargs["data"]["client_secret"] == "secret"


def test_get_oauth_token_http_error(service):
    """Simula error HTTP en la obtención del token."""
    fake_response = MagicMock()
    fake_response.raise_for_status.side_effect = HTTPError("fail")
    with patch(
        REQUEST_POST,
        return_value=fake_response,
    ):
        with pytest.raises(HTTPError):
            service._get_oauth_token("id", "secret")


@patch(REQUEST_POST)
def test_call_prestamo_service_success_devuelve_json_en_2xx(mock_post, service):
    """En status 2xx, el método devuelve el JSON con los datos (no un dict de error)."""
    fake_response = MagicMock()
    fake_response.status_code = 200
    fake_response.json.return_value = {"gastos": 1234.56}
    mock_post.return_value = fake_response

    token = "fake_token"
    data = {"importe": 100000, "tipo": "hip", "zonaGeo": "Sevilla"}

    result = service._call_prestamo_service(token, data)

    assert result == {"gastos": 1234.56}
    mock_post.assert_called_once()
    _, kwargs = mock_post.call_args
    assert kwargs["headers"]["Authorization"] == f"Bearer {token}"
    assert kwargs["json"] == data


@patch(REQUEST_POST)
def test_call_prestamo_service_http_error_devuelve_error(mock_post, service):
    """En status != 2xx, el método devuelve dict con 'error' incluyendo código y cuerpo JSON."""
    fake_response = MagicMock()
    fake_response.status_code = 500
    fake_response.json.return_value = {"detalle": FALLO_API}
    mock_post.return_value = fake_response

    result = service._call_prestamo_service("token", {"param": 1})

    assert isinstance(result, dict)
    assert "error" in result
    assert "HTTP error occurred: 500" in result["error"]
    assert (
        str({"detalle": FALLO_API}) in result["error"]
    )  # el cuerpo JSON se incluye en el mensaje


@patch(REQUEST_POST)
def test_call_prestamo_service_http_error_no_json(mock_post, service):
    """En status != 2xx con cuerpo no JSON, devuelve dict con 'error' incluyendo texto plano."""
    fake_response = MagicMock()
    fake_response.status_code = 503
    # Simular que .json() lanza ValueError para indicar cuerpo no JSON
    fake_response.json.side_effect = ValueError("no-json")
    fake_response.text = "plain-text"
    mock_post.return_value = fake_response

    result = service._call_prestamo_service("token", {"importe": 1000})

    assert isinstance(result, dict)
    assert "error" in result
    assert "HTTP error occurred: 503" in result["error"]


@pytest.fixture
def service():
    """Instancia del servicio con configuración parcheada."""
    with patch(
        "app.services.gastos_hipotecarios_service.UnicajaServicesConfig"
    ) as mock_config:
        mock_instance = mock_config.return_value
        mock_instance.client_id = "fake_id"
        mock_instance.client_secret = "fake_secret"
        mock_instance.url_token_oauth2 = "https://fake.token.url"
        mock_instance.api_gastos_hipotecarios = "https://fake.api.url"
        yield GastosHipotecariosService()


def test_get_oauth_token_success(service):
    """Prueba que se obtiene el token correctamente."""
    fake_response = MagicMock()
    fake_response.json.return_value = {"access_token": "fake_token"}
    fake_response.raise_for_status.return_value = None

    with patch(REQUEST_POST, return_value=fake_response):
        token = service._get_oauth_token("id", "secret")
        assert token == "fake_token"


def test_get_oauth_token_http_error(service):
    """Simula error HTTP al obtener el token."""
    fake_response = MagicMock()
    fake_response.raise_for_status.side_effect = HTTPError("fail")

    with patch(REQUEST_POST, return_value=fake_response):
        with pytest.raises(HTTPError):
            service._get_oauth_token("id", "secret")


def test_call_success(service):
    """Prueba completa del método call con mocks."""
    with patch.object(
        service, "_get_oauth_token", return_value="token"
    ) as mock_token, patch.object(
        service, "_call_prestamo_service", return_value={"gastos": 1234}
    ) as mock_call:

        result = service.call(100000, 2, "23")
        assert result == {"gastos": 1234}
        mock_token.assert_called_once_with("fake_id", "fake_secret")
        mock_call.assert_called_once()
        args, _ = mock_call.call_args
        assert args[0] == "token"
        assert args[1] == {"importe": 100000, "tipo": "hip", "zonaGeo": "an"}


def test_call_handles_exception(service):
    """Prueba que call captura excepciones y devuelve mensaje de error."""
    with patch.object(service, "_get_oauth_token", side_effect=Exception("fail")):
        result = service.call(100000, 2, "23")
        assert isinstance(result, str)
        assert "Error:" in result
