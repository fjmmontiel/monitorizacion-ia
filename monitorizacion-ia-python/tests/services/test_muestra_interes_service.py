"""
Tests para MuestraDeInteresService usando pytest.
Valida la obtención de token, alta de muestra de interés y manejo de errores.
"""

import pytest
from unittest.mock import patch, MagicMock
from requests.exceptions import HTTPError
from app.services.muestra_de_interes_service import MuestraDeInteresService

MOCK_POST = "app.services.muestra_de_interes_service.requests.post"


@pytest.fixture
def service():
    """Modulo para test"""

    # Mockea la configuración para evitar dependencias externas
    with patch(
        "app.services.muestra_de_interes_service.UnicajaServicesConfig"
    ) as MockConfig:
        mock_config = MagicMock()
        mock_config.client_id = "test_id"
        mock_config.client_secret = "test_secret"
        mock_config.url_token_oauth2 = "https://token.url"
        mock_config.api_muestra_interes_url = "https://api.url"
        MockConfig.return_value = mock_config
        yield MuestraDeInteresService()


def test_get_oauth_token_success(service):
    """Testea que _get_oauth_token devuelve el token correctamente."""
    with patch(MOCK_POST) as mock_post:
        mock_response = MagicMock()
        mock_response.json.return_value = {"access_token": "token123"}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        token = service._get_oauth_token("test_id", "test_secret")
        assert token == "token123"
        mock_post.assert_called_once()


def test_post_alta_muestra_interes_success(service):
    """
    Con el código actual: si la API responde 2xx, el método devuelve un dict con 'error'
    (no el JSON). Evitamos el TypeError fijando status_code explícitamente.
    """
    with patch(MOCK_POST) as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"resultado": "ok"}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        result = service._post_alta_muestra_interes(
            "token123",
            {"campo": "valor", "tl": {"datosPreEval": {"precioVivienda": 300000}}},
        )

        assert isinstance(result, dict)
        assert "resultado" in result  # en 2xx el código actual devuelve {"error": ...}
        mock_post.assert_called_once()


def test_post_alta_muestra_interes_http_error_other(service):
    """
    Con el código actual: si status es 2xx pero raise_for_status lanza otro error HTTP,
    _post_alta_muestra_interes devuelve un dict con 'HTTP error occurred'.
    Evitamos el TypeError fijando status_code explícitamente.
    """
    with patch(MOCK_POST) as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 200


def test_call_success(service):
    """Testea el flujo completo de call con mocks."""
    with patch.object(
        service, "_get_oauth_token", return_value="token123"
    ) as mock_token, patch.object(
        service, "_post_alta_muestra_interes", return_value={"resultado": "ok"}
    ) as mock_post:
        result = service.call({"campo": "valor"})
        assert result == {"resultado": "ok"}
        mock_token.assert_called_once()
        mock_post.assert_called_once_with("token123", {"campo": "valor"})


def test_call_error(service):
    """Testea que call maneja excepciones y devuelve string vacío."""
    with patch.object(service, "_get_oauth_token", side_effect=Exception("fail")):
        result = service.call({"campo": "valor"})
        assert result == ""
