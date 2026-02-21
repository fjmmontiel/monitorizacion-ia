"""Modulo para test"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch

from main import app
from qgdiag_lib_arquitectura.security import authentication

client = TestClient(app)


@pytest.mark.asyncio
async def test_on_startup(monkeypatch):
    """Debe inicializar jwks_store en app.state durante el startup"""

    # Mock settings.get_jwks para devolver None
    monkeypatch.setattr("app.settings.Settings.get_jwks", lambda self: None)

    # Mock authentication.fetch_jwks como async
    async def fake_fetch_jwks(channel):
        """Modulo"""
        return {"keys": ["fake"]}

    monkeypatch.setattr("main.authentication.fetch_jwks", fake_fetch_jwks)

    # Mock Authenticator para devolver un objeto simulado
    class FakeAuthenticator:
        """Modulo"""

        def __init__(self, jwks):
            self.jwks = jwks

    monkeypatch.setattr("main.authentication.Authenticator", FakeAuthenticator)

    # Ejecutar el ciclo de startup completo
    await app.router.startup()

    # Verificar que el jwks_store se guardó en app.state
    assert hasattr(app.state, "jwks_store")
    assert isinstance(app.state.jwks_store, FakeAuthenticator)
    assert app.state.jwks_store.jwks == {"keys": ["fake"]}
