"""Tests para el servicio de gastos de tasación."""

import pytest
from unittest.mock import patch, MagicMock
from requests.exceptions import HTTPError

from app.services.gastos_tasacion_service import GastosTasacionService

REQUEST_POST = "app.services.gastos_tasacion_service.requests.post"


@pytest.fixture
def service():
    """Instancia del servicio con configuración parcheada."""
    with patch(
        "app.services.gastos_tasacion_service.UnicajaServicesConfig"
    ) as mock_config:
        mock_instance = mock_config.return_value
        mock_instance.client_id = "fake_id"
        mock_instance.client_secret = "fake_secret"
        mock_instance.url_token_oauth2 = "https://fake.token.url"
        mock_instance.api_gastos_tasacion = "https://fake.api.url"
        yield GastosTasacionService()


def test_get_oauth_token_success(service):
    """Prueba que se obtiene token correctamente."""
    fake_response = MagicMock()
    fake_response.json.return_value = {"access_token": "fake_token"}
    fake_response.raise_for_status.return_value = None

    with patch(REQUEST_POST, return_value=fake_response) as mock_post:
        token = service._get_oauth_token("id", "secret")
        assert token == "fake_token"
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        assert kwargs["data"]["client_id"] == "id"
        assert kwargs["data"]["client_secret"] == "secret"


def test_get_oauth_token_http_error(service):
    """Prueba que se lanza HTTPError correctamente."""
    fake_response = MagicMock()
    fake_response.raise_for_status.side_effect = HTTPError("fail")

    with patch(REQUEST_POST, return_value=fake_response):
        with pytest.raises(HTTPError):
            service._get_oauth_token("id", "secret")


def test_call_success(service):
    """Prueba método call devuelve el valor correcto."""
    with patch.object(
        service, "_get_oauth_token", return_value="token"
    ) as mock_token, patch.object(
        service,
        "_call_simulacion_service",
        return_value={"datosSimulacion": {"impTasacion": 5000}},
    ) as mock_call:

        result = service.call(
            precio_vivienda=100000,
            provincia="Sevilla",
            indicador_vivienda_habitual="S",
            tipo_vivienda=1,
            fecha_nacimiento="1990-01-01",
            ingresos=30000,
        )
        assert result == 5000
        mock_token.assert_called_once_with(service.client_id, service.client_secret)
        mock_call.assert_called_once()


@patch(REQUEST_POST)
def test_call_simulacion_service_success_devuelve_json_en_2xx(mock_post, service):
    """En status 2xx, _call_simulacion_service devuelve el JSON (no un dict de error)."""
    fake_response = MagicMock()
    fake_response.status_code = 200
    fake_response.json.return_value = {"datosSimulacion": {"impTasacion": 1234.56}}
    mock_post.return_value = fake_response

    token = "fake_token"
    params = {"any": "param"}
    result = service._call_simulacion_service(token, params)

    assert result == {"datosSimulacion": {"impTasacion": 1234.56}}
    mock_post.assert_called_once()
    _, kwargs = mock_post.call_args


def test_call_handles_exception(service):
    """Prueba método call maneja excepciones y devuelve mensaje de error."""
    with patch.object(service, "_get_oauth_token", side_effect=Exception("fail")):
        result = service.call(
            precio_vivienda=100000,
            provincia="Sevilla",
            indicador_vivienda_habitual="S",
            tipo_vivienda=1,
            fecha_nacimiento="1990-01-01",
            ingresos=30000,
        )
        assert "Error: fail" in result
