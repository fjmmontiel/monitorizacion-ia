"""Tests para el servicio de log operacional."""

import pytest
import requests
from unittest.mock import patch, MagicMock
from requests.exceptions import HTTPError, RequestException
from app.services.log_operacional_service import LogOperacionalService
from app.models.models_APIRequest import LogOperacionalRequest

# ---------- CONSTANTES ----------

MOCK_API_URL = "https://fake.api.url"
MOCK_TOKEN = "mock_token_123"
PATH_POST = "app.services.log_operacional_service.requests.post"
LOG_CORRECTO = "Log registrado correctamente"
TIMESTAMP_INICIO = "2024-01-15T10:00:00"
TIMESTAMP_FIN = "2024-01-15T10:05:00"
TEST_PATH = "/api/test/path"
CONNECTION_TIMEOUT = "Connection timeout"


@pytest.fixture
def mock_config():
    """Configura mock de UnicajaServicesConfig con valores predefinidos."""
    with patch(
        "app.services.log_operacional_service.UnicajaServicesConfig"
    ) as mock_conf:
        mock_instance = mock_conf.return_value
        mock_instance.api_log_operacional = MOCK_API_URL
        yield mock_instance


@pytest.fixture
def mock_headers():
    """Headers de prueba para el servicio."""
    return {
        "Token": MOCK_TOKEN,
        "Channel": "interno",
        "Content-Type": "application/json",
        "Accept": "*/*",
    }


@pytest.fixture
def mock_requests_post():
    """Mock para requests.post con respuesta exitosa predefinida."""
    with patch(PATH_POST) as mock_post:
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "status": "Success",
            "message": LOG_CORRECTO,
        }
        mock_response.raise_for_status.return_value = None
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        yield mock_post


@pytest.fixture
def mock_log_request():
    """Fixture con datos de LogOperacionalRequest para testing."""
    return LogOperacionalRequest(
        codGestor="TEST001",
        timestampInicio=TIMESTAMP_INICIO,
        timestampFin=TIMESTAMP_FIN,
        claper="BBB03333",
        httpMethod="POST",
        modulo="OPERACIONES",
        seccion="HIPOTECAS",
        operacion="TEST_OPERATION",
        path=TEST_PATH,
        request='{"test": "data"}',
        response='{"status": "success"}',
        status="200",
    )


@pytest.fixture
def service_instance(mock_config, mock_headers):
    """Instancia del servicio con configuración mockeada."""
    return LogOperacionalService(mock_headers)


# ---------- TESTS LogOperacionalService ----------


class TestLogOperacionalService:
    """Tests para la inicialización y configuración del servicio."""

    def test_init_success(self, service_instance, mock_headers):
        """Verifica que la inicialización del servicio sea correcta."""
        assert service_instance.api_url == MOCK_API_URL
        assert service_instance.headers == mock_headers
        assert service_instance.headers["Token"] == MOCK_TOKEN

    def test_init_config_attributes(self, mock_config, mock_headers):
        """Verifica que se asignen correctamente los atributos de configuración."""
        service = LogOperacionalService(mock_headers)

        assert hasattr(service, "api_url")
        assert hasattr(service, "headers")
        assert service.api_url == MOCK_API_URL
        assert service.headers == mock_headers

    def test_init_with_different_headers(self, mock_config):
        """Verifica que el servicio acepta diferentes headers."""
        custom_headers = {"Token": "custom_token_456", "CustomHeader": "custom_value"}
        service = LogOperacionalService(custom_headers)

        assert service.headers == custom_headers
        assert service.headers["Token"] == "custom_token_456"


class TestRegistrarLog:
    """Tests para el método _registrar_log."""

    def test_registrar_log_success(self, service_instance, mock_log_request):
        """Verifica registro exitoso de log."""
        with patch(PATH_POST) as mock_post:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "status": "Success",
                "message": "Log registrado",
            }
            mock_response.status_code = 200
            mock_post.return_value = mock_response

            result = service_instance._registrar_log(mock_log_request)

            # Verificar que se llamó con los headers correctos
            expected_headers = {
                "Channel": "interno",
                "Connection": "keep-alive",
                "Content-Type": "application/json",
                "Token": MOCK_TOKEN,
                "Accept": "*/*",
            }

            mock_post.assert_called_once_with(
                MOCK_API_URL,
                headers=expected_headers,
                json=mock_log_request.model_dump(),
            )

            assert result == {"status": "Success", "message": "Log registrado"}

    def test_registrar_log_http_error_4xx(self, service_instance, mock_log_request):
        """Verifica manejo de error HTTP 4xx."""
        with patch(PATH_POST) as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 400
            mock_response.json.return_value = {"error": "Bad request"}
            mock_post.return_value = mock_response

            result = service_instance._registrar_log(mock_log_request)

            assert "error" in result
            assert "HTTP error occurred: 400" in result["error"]
            assert "Bad request" in result["error"]

    def test_registrar_log_http_error_5xx(self, service_instance, mock_log_request):
        """Verifica manejo de error HTTP 5xx."""
        with patch(PATH_POST) as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 500
            mock_response.json.return_value = {"error": "Internal server error"}
            mock_post.return_value = mock_response

            result = service_instance._registrar_log(mock_log_request)

            assert "error" in result
            assert "HTTP error occurred: 500" in result["error"]

    def test_registrar_log_http_error_non_json_response(
        self, service_instance, mock_log_request
    ):
        """Verifica manejo de error con respuesta no JSON."""
        with patch(PATH_POST) as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 404
            mock_response.json.side_effect = ValueError("No JSON")
            mock_response.text = "Not Found"
            mock_post.return_value = mock_response

            result = service_instance._registrar_log(mock_log_request)

            assert "error" in result
            assert "HTTP error occurred: 404" in result["error"]
            assert "Not Found" in result["error"]

    def test_registrar_log_success_non_json_response(
        self, service_instance, mock_log_request
    ):
        """Verifica manejo de respuesta exitosa pero no JSON."""
        with patch(PATH_POST) as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.side_effect = ValueError("No JSON")
            mock_response.text = "Success but not JSON"
            mock_post.return_value = mock_response

            result = service_instance._registrar_log(mock_log_request)

            assert "error" in result
            assert "Respuesta no JSON" in result["error"]
            assert "Success but not JSON" in result["error"]

    @patch("app.services.log_operacional_service.logger")
    def test_registrar_log_logs_info(
        self, mock_logger, service_instance, mock_log_request
    ):
        """Verifica que se loguee la llamada al servicio."""
        with patch(PATH_POST) as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"status": "Success"}
            mock_post.return_value = mock_response

            service_instance._registrar_log(mock_log_request)

            mock_logger.info.assert_called_with(
                "Llamada a servicio para registrar log operacional"
            )


class TestCallMethod:
    """Tests para el método call."""

    def test_call_success(self, service_instance, mock_log_request):
        """Verifica llamada exitosa completa."""
        with patch.object(service_instance, "_registrar_log") as mock_registrar:
            mock_registrar.return_value = {
                "status": "Success",
                "message": LOG_CORRECTO,
            }

            result = service_instance.call(mock_log_request)

            mock_registrar.assert_called_once_with(mock_log_request)
            assert LOG_CORRECTO in result
            assert LOG_CORRECTO in result

    def test_call_unexpected_response(self, service_instance, mock_log_request):
        """Verifica manejo de respuesta inesperada."""
        with patch.object(service_instance, "_registrar_log") as mock_registrar:
            mock_registrar.return_value = {"unexpected": "response"}

            result = service_instance.call(mock_log_request)

            assert "Respuesta inesperada" in result
            assert "unexpected" in result

    def test_call_error_in_registrar_log(self, service_instance, mock_log_request):
        """Verifica manejo de errores en _registrar_log."""
        with patch.object(service_instance, "_registrar_log") as mock_registrar:
            mock_registrar.return_value = {
                "error": "HTTP error occurred: 500 - Server error"
            }

            result = service_instance.call(mock_log_request)

            assert "Respuesta inesperada" in result
            assert "error" in result

    def test_call_exception_handling(self, service_instance, mock_log_request):
        """Verifica manejo de excepciones en call."""
        with patch.object(service_instance, "_registrar_log") as mock_registrar:
            mock_registrar.side_effect = Exception(CONNECTION_TIMEOUT)

            result = service_instance.call(mock_log_request)

            assert "error" in result
            assert CONNECTION_TIMEOUT in result["error"]

    @patch("app.services.log_operacional_service.logger")
    def test_call_logs_error_on_exception(
        self, mock_logger, service_instance, mock_log_request
    ):
        """Verifica que se logueen los errores de excepción."""
        with patch.object(service_instance, "_registrar_log") as mock_registrar:
            mock_registrar.side_effect = Exception("Test exception")

            service_instance.call(mock_log_request)

            mock_logger.info.assert_any_call(
                "[ERROR] Fallo en el flujo de registro de log: Test exception"
            )


class TestEdgeCases:
    """Tests para casos límite y situaciones especiales."""

    def test_empty_headers(self, mock_config):
        """Verifica comportamiento con headers vacíos."""
        empty_headers = {}
        service = LogOperacionalService(empty_headers)

        assert service.headers == empty_headers

        # Debería fallar al intentar acceder al token
        mock_log_request = LogOperacionalRequest(
            codGestor="TEST001",
            timestampInicio=TIMESTAMP_INICIO,
            timestampFin=TIMESTAMP_FIN,
            claper="BBB03333",
            httpMethod="POST",
            modulo="test",
            seccion="HIPOTECAS",
            operacion="test",
            path=TEST_PATH,
            response="{}",
            status="200",
        )

        with patch(PATH_POST) as mock_post:
            with pytest.raises(KeyError):  # No hay Token en headers vacíos
                service._registrar_log(mock_log_request)

    def test_none_headers(self, mock_config):
        """Verifica comportamiento con headers None."""
        service = LogOperacionalService(None)

        assert service.headers is None

        mock_log_request = LogOperacionalRequest(
            codGestor="TEST001",
            timestampInicio=TIMESTAMP_INICIO,
            timestampFin=TIMESTAMP_FIN,
            claper="BBB03333",
            httpMethod="POST",
            modulo="test",
            seccion="HIPOTECAS",
            operacion="test",
            path=TEST_PATH,
            response="{}",
            status="200",
        )

        with patch(PATH_POST) as mock_post:
            with pytest.raises(TypeError):  # None no es subscriptable
                service._registrar_log(mock_log_request)

    def test_large_log_data(self, service_instance):
        """Verifica manejo de datos de log muy grandes."""
        large_log_request = LogOperacionalRequest(
            codGestor="TEST001",
            timestampInicio=TIMESTAMP_INICIO,
            timestampFin=TIMESTAMP_FIN,
            claper="BBB03333",
            httpMethod="POST",
            modulo="test_module",
            seccion="HIPOTECAS",
            operacion="test_operation",
            path=TEST_PATH,
            response="A" * 10000,  # Respuesta muy larga
            status="200",
        )

        with patch(PATH_POST) as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"status": "Success"}
            mock_post.return_value = mock_response

            result = service_instance._registrar_log(large_log_request)

            # Debería manejar datos grandes sin problemas
            assert "status" in result
            mock_post.assert_called_once()

    def test_request_timeout(self, service_instance, mock_log_request):
        """Verifica manejo de timeout en la petición."""
        with patch(PATH_POST) as mock_post:
            mock_post.side_effect = RequestException(CONNECTION_TIMEOUT)

            # Aunque el método no tiene manejo explícito de timeout,
            # debería propagar la excepción que luego es capturada en call()
            with pytest.raises(RequestException):
                service_instance._registrar_log(mock_log_request)

    def test_malformed_log_request(self, service_instance):
        """Verifica manejo de LogOperacionalRequest mal formado."""
        # Crear un mock que simule un request mal formado
        malformed_request = MagicMock()
        malformed_request.model_dump.side_effect = Exception("Serialization error")

        with patch(PATH_POST) as mock_post:
            with pytest.raises(Exception):  # Debería fallar en model_dump()
                service_instance._registrar_log(malformed_request)
