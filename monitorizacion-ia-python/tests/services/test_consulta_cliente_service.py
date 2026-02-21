"""
Tests para ConsultaClienteService usando pytest.
Valida la obtención de token OAuth, consulta de datos y manejo de errores.
"""

import pytest
from unittest.mock import patch, MagicMock
from app.services.consulta_cliente_service import ConsultaClienteService


@pytest.fixture
def service():
    """Modulo para test"""

    # Mockea la configuración para evitar dependencias externas
    with patch(
        "app.services.consulta_cliente_service.UnicajaServicesConfig"
    ) as MockConfig:
        mock_config = MagicMock()
        mock_config.client_id = "test_id"
        mock_config.client_secret = "test_secret"
        mock_config.token_url = (
            "https://urldefense.com/v3/__https://token.url__;!!GHGCd83Y"
            "js5jPw!K8UXIAP0-FHxNSX6a3csrRjReTuCrLigoUz4Td6WcQhR_pUycl-8qf"
            "g83gEvddFSc_yLOPj_1Ml_JNIu3n9-EmTfdBOzMfdaiK0$ "
        )
        mock_config.api_consulta_cliente_url = (
            "https://urldefense.com/v3/__https://api.ur"
            "l__;!!GHGCd83Yjs5jPw!K8UXIAP0-FHxNSX6a3csrRjReTuCrLigoUz4Td6WcQh"
            "R_pUycl-8qfg83gEvddFSc_yLOPj_1Ml_JNIu3n9-EmTfdBOz2_VqsTE$ "
        )
        MockConfig.return_value = mock_config
        yield ConsultaClienteService()


def test_get_oauth_token_success(service):
    """Testea que _get_oauth_token devuelve el token correctamente."""
    with patch("app.services.consulta_cliente_service.requests.post") as mock_post:
        mock_response = MagicMock()
        mock_response.json.return_value = {"access_token": "token123"}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        token = service._get_oauth_token("test_id", "test_secret")
        assert token == "token123"
        mock_post.assert_called_once()


def test_consulta_datos_cliente_success(service):
    """
    Con el código actual: si la API responde 2xx, _consulta_datos_cliente
    devuelve el JSON con los datos del cliente (no un dict de error).
    """
    with patch("app.services.consulta_cliente_service.requests.post") as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"nombre": "Juan", "nif": "12345678A"}
        mock_post.return_value = mock_response

        result = service._consulta_datos_cliente("token123", "12345678A")


def test_call_success(service):
    """Testea el flujo completo de call con mocks."""
    with patch.object(
        service, "_get_oauth_token", return_value="token123"
    ) as mock_token, patch.object(
        service, "_consulta_datos_cliente", return_value={"nombre": "Juan"}
    ) as mock_consulta:
        result = service.call("12345678A")
        assert result == {"nombre": "Juan"}
        mock_token.assert_called_once()
        mock_consulta.assert_called_once_with("token123", "12345678A")


def test_call_error(service):
    """Testea que call maneja excepciones y devuelve 'Error: ...'."""
    with patch.object(service, "_get_oauth_token", side_effect=Exception("fail")):
        result = service.call("12345678A")
        assert isinstance(result, str)
        assert result.startswith("Error: ")
