"""
Configuración de pruebas para FastAPI.
"""

import os
import sys

import pytest
from fastapi.testclient import TestClient

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
)

 
from qgdiag_lib_arquitectura.security.authentication import get_authenticated_headers

from main import app


@pytest.fixture(autouse=True)
def mock_auth():
    """
    Sustituye get_authenticated_headers para que siempre incluya:
      "IAG-App-Id": "app_test"
    """

    def mock_get_authenticated_headers():
        """Mocks get_authenticated_headers"""
        return {
            "Token": "dummy-token",
            "IAG-App-Id": "app_test",
            "sub": "test_user",
        }

    app.dependency_overrides[get_authenticated_headers] = mock_get_authenticated_headers
    yield
    app.dependency_overrides.pop(get_authenticated_headers, None)


@pytest.fixture(scope="session")
def client():
    """
    Cliente compartido para las pruebas.
    """
    with TestClient(app) as c:
        yield c
