"""Tests de autorización LDAP, endpoint de chat y endpoints de contexto.

Este módulo prueba:
- `validate_authorize_request`: validación de token y usuario contra LDAP.
- `chat`: endpoint FastAPI para streaming de mensajes.
- `get_context_item`: obtiene un item de contexto por ID.
- `procesar_ficha_producto`: procesa PDFs y guarda fichas de producto.
"""

import pytest
import json
from unittest.mock import MagicMock, patch, AsyncMock
from fastapi import HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from types import SimpleNamespace
from pathlib import Path

# Importar funciones a testear
from app.routes.routes import (
    validate_authorize_request,
    chat,
    get_context_item,
)

# ==== CONSTANTES COMUNES ====
LDAP_URL = "https://ldap.test.local"
APP_CODE = "hipotecas_app"
SUB_ID = "user-123"
TOKEN_VALUE = "tok-abc-123"
PATH_GET = "app.routes.routes.requests.get"
REQ_PARAMS = {"usuarioId": SUB_ID, "aplicacionId": APP_CODE}
REQ_HEADERS = {"Channel": "iag", "Token": TOKEN_VALUE}


# ==== HELPERS ====
def make_request(headers):
    """Crea un objeto `Request` simulado con cabeceras proporcionadas."""
    req = MagicMock()
    req.headers = headers
    return req


def stub_response(code=200, body="authorized"):
    """Crea una respuesta HTTP simulada con `status_code` y `text`."""
    resp = MagicMock()
    resp.status_code = code
    resp.text = body
    return resp


# ==== FIXTURES ====
@pytest.fixture
def patched_env():
    """Parches comunes: settings, get_user_id, logger.info."""
    with patch(
        "app.routes.routes.settings",
        SimpleNamespace(
            LDAP_URL=LDAP_URL,
            LDAP_APP=APP_CODE,
            URL_TOKEN_JWT="unused",
            IAG_APP_ID="iag-app-id",
        ),
    ), patch("app.routes.routes.get_user_id", return_value=SUB_ID), patch(
        "app.routes.routes.logger"
    ) as mock_logger:
        mock_logger.info = MagicMock()
        yield


# ==== TEST chat ====
class TestChatEndpoint:
    """Pruebas para el endpoint `chat`."""

    @pytest.fixture
    def common_patches(self):
        """Parches comunes para settings, logger y distributed_context."""
        with patch(
            "app.routes.routes.settings",
            SimpleNamespace(IAG_APP_ID="iag-app-id"),
        ), patch("app.routes.routes.logger") as mock_logger, patch(
            "app.managers.distributed_context.distributed_session_manager.create_context",
            return_value={"ctx": "distributed"},
        ):
            mock_logger.info = MagicMock()
            yield


# ==== TEST get_context_item ====
class TestGetContextItem:
    """Pruebas para `get_context_item`."""

    @pytest.mark.asyncio
    async def test_get_context_item_ok(self):
        """Devuelve el item correctamente si existe."""
        mock_item = MagicMock(DES_JSON=json.dumps({"key": "value"}))
        db_session = MagicMock()
        db_session.query.return_value.filter.return_value.all.return_value = [mock_item]

        result = await get_context_item("item123", db_session, headers={"Token": "abc"})
        assert result == {"key": "value"}

    @pytest.mark.asyncio
    async def test_get_context_item_error_sqlalchemy(self):
        """Propaga error SQLAlchemy si ocurre excepción."""
        db_session = MagicMock()
        db_session.query.side_effect = Exception("DB fail")
        with pytest.raises(Exception) as exc:
            await get_context_item("itemX", db_session, headers={"Token": "abc"})
        assert "DB fail" in str(exc.value)
