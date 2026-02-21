"""Modulo para tests"""

import pytest
from unittest.mock import patch, MagicMock
from requests.exceptions import HTTPError

from app.services.muestra_de_interes_service_cancelacion import (
    CancelacionMuestraDeInteresService,
)

REQUEST_POST = "app.services.muestra_de_interes_service_cancelacion.requests.post"


@pytest.fixture
def service():
    """Instancia del servicio con configuración parcheada."""
    with patch(
        "app.services.muestra_de_interes_service_cancelacion.UnicajaServicesConfig"
    ) as mock_config:
        mock_instance = mock_config.return_value
        mock_instance.client_id = "fake_id"
        mock_instance.client_secret = "fake_secret"
        mock_instance.url_token_oauth2 = "https://fake.token.url"
        mock_instance.api_cancelar_muestra_interes_url = "https://fake.api.url"
        yield CancelacionMuestraDeInteresService()


def test_get_oauth_token_success(service):
    """Prueba que se obtiene el token correctamente."""
    fake_response = MagicMock()
    fake_response.json.return_value = {"access_token": "fake_token"}
    fake_response.raise_for_status.return_value = None

    with patch(REQUEST_POST, return_value=fake_response) as mock_post:
        token = service._get_oauth_token("id", "secret")
        assert token == "fake_token"
        mock_post.assert_called_once()
        _, kwargs = mock_post.call_args
        assert kwargs["data"]["client_id"] == "id"
        assert kwargs["data"]["client_secret"] == "secret"


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
        service, "_post_cancelar_muestra_interes", return_value={"status": "cancelled"}
    ) as mock_post:

        result = service.call("2025224800000085")
        assert result == {"status": "cancelled"}
        mock_token.assert_called_once_with("fake_id", "fake_secret")
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        assert args[0] == "token"
        assert args[1]["numeroExpediente"] == "2025224800000085"


def test_post_cancelar_muestra_interes_http_error_with_json(service):
    """412 ⇒ devuelve dict con 'error' y mensaje específico."""
    fake_response = MagicMock()
    fake_response.status_code = 412
    fake_response.json.return_value = {"detail": "Some error"}

    with patch(REQUEST_POST, return_value=fake_response):
        result = service._post_cancelar_muestra_interes(
            "token", {"numeroExpediente": "123456"}
        )
        assert isinstance(result, dict)
        assert result == {
            "error": "HTTP error occurred: 412 - No se puede cancelar la muestra de interés."
        }


def test_post_cancelar_muestra_interes_http_error_non_json(service):
    """Status no 2xx con cuerpo no JSON ⇒ 'error' con texto del body."""
    fake_response = MagicMock()
    fake_response.status_code = 500
    fake_response.json.side_effect = ValueError("No JSON")
    fake_response.text = "Internal Server Error"

    with patch(REQUEST_POST, return_value=fake_response):
        result = service._post_cancelar_muestra_interes(
            "token", {"numeroExpediente": "123456"}
        )
        assert isinstance(result, dict)
        assert "error" in result
        assert "500" in result["error"]
        assert "Internal Server Error" in result["error"]


@patch(REQUEST_POST)
def test_post_cancelar_muestra_interes_success(mock_post, service):
    """2xx ⇒ devuelve JSON del éxito."""
    fake_response = MagicMock()
    fake_response.status_code = 200
    fake_response.json.return_value = {"status": "cancelled"}
    mock_post.return_value = fake_response

    result = service._post_cancelar_muestra_interes(
        "token", {"numeroExpediente": "123456"}
    )
    assert isinstance(result, dict)
    assert result == {"status": "cancelled"}
    mock_post.assert_called_once()


@patch(REQUEST_POST)
def test_post_cancelar_muestra_interes_http_error(mock_post, service):
    """Status no 2xx con cuerpo JSON ⇒ devuelve dict con 'error' y el JSON serializado en el mensaje."""
    fake_response = MagicMock()
    fake_response.status_code = 500
    fake_response.json.return_value = {"detalle": "fallo api"}
    mock_post.return_value = fake_response

    result = service._post_cancelar_muestra_interes(
        "token", {"numeroExpediente": "123456"}
    )
    assert isinstance(result, dict)
    assert "error" in result
    assert "500" in result["error"]
    # El cuerpo JSON se inserta como dict en el string:
    assert "{'detalle': 'fallo api'}" in result["error"]
