"""Tests ampliados para el servicio de generación del documento de la muestra de interés."""

import pytest
import unittest
from unittest.mock import patch, MagicMock
from requests.exceptions import HTTPError

from app.services.muestra_de_interes_service_documento import DocMuestraDeInteresService

REQUEST_POST = "app.services.muestra_de_interes_service_documento.requests.post"


@pytest.fixture
def service():
    """Instancia del servicio con configuración parcheada."""
    with patch(
        "app.services.muestra_de_interes_service_documento.UnicajaServicesConfig"
    ) as mock_config:
        mock_instance = mock_config.return_value
        mock_instance.client_id = "fake_id"
        mock_instance.client_secret = "fake_secret"
        mock_instance.url_token_oauth2 = "https://fake.token.url"
        mock_instance.api_doc_muestra_interes_url = "https://fake.api.url"
        yield DocMuestraDeInteresService()


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
        _, kwargs = mock_post.call_args
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


def test_call_success(service):
    """Prueba método call devuelve respuesta correcta usando mocks internos."""
    with patch.object(
        service, "_get_oauth_token", return_value="token"
    ) as mock_token, patch.object(
        service, "_post_alta_doc_muestra_interes", return_value="OK"
    ) as mock_post:

        result = service.call("123456")
        assert result == "OK"
        mock_token.assert_called_once_with(service.client_id, service.client_secret)
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        assert args[0] == "token"
        # Verifica que el payload contiene el expediente correcto
        assert args[1]["numExpediente"] == "123456"
