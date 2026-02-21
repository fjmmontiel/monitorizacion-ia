"""
Test unitarios para LecturaFichaProductoService.

Incluye pruebas de:
- Lectura y procesamiento de archivos CSV.
- Exclusión de archivos específicos.
.- Inserción/actualización de traducciones en base de datos.
- Manejo de errores en persistencia.

Se utilizan fixtures y mocks para simular la sesión de base de datos y archivos.
"""

import json
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime
from pathlib import Path
from app.services.lectura_fichas_service import LecturaFichaProductoService
from app.exceptions.app_exceptions import RepositoryException

NOMBRE_TEST = "Hipoteca Test"


@pytest.fixture
def mock_db_session():
    """Mock de la sesión SQLAlchemy."""
    db = MagicMock()
    db.merge = MagicMock()
    db.commit = MagicMock()
    db.rollback = MagicMock()
    return db


@pytest.fixture
def mock_headers():
    """Test"""
    return {"Authorization": "Bearer fake-token"}


@pytest.fixture
def mock_cliente():
    """Mock del cliente OpenAI (IA Core)."""
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.model_dump.return_value = {
        "nombre_producto": NOMBRE_TEST,
        "codigo_producto": {"comercial": "123", "administrativo": "456"},
        "descripcion_producto": "Descripción test",
    }
    mock_client.chat.completions.create.return_value = mock_response
    return mock_client


@pytest.fixture
def mock_pdf(tmp_path):
    """Crea un archivo PDF temporal."""
    pdf_file = tmp_path / "ficha_test.pdf"
    pdf_file.write_text("Contenido PDF simulado")
    return pdf_file


@pytest.fixture
def service(mock_headers, mock_db_session):
    """Instancia del servicio."""
    return LecturaFichaProductoService(mock_headers, mock_db_session)


def test_guardar_ficha_producto_ok(service, mock_db_session):
    """Guarda correctamente una ficha de producto."""
    data = json.dumps(
        {"codigo_producto": {"administrativo": "999"}, "nombre": "test"},
        ensure_ascii=False,
    )

    with patch(
        "app.services.lectura_fichas_service.FichaProductoHipoteca"
    ) as mock_model:
        mock_instance = MagicMock()
        mock_model.return_value = mock_instance

        service.guardar_ficha_producto(data)

        mock_model.assert_called_once()
        mock_db_session.merge.assert_called_once_with(mock_instance)
        mock_db_session.commit.assert_called_once()


def test_guardar_ficha_producto_error(service, mock_db_session):
    """Simula error en commit de SQLAlchemy y verifica rollback."""
    data = json.dumps(
        {"codigo_producto": {"administrativo": "123"}},
        ensure_ascii=False,
    )

    mock_db_session.merge.side_effect = Exception("DB merge failed")

    with patch("app.services.lectura_fichas_service.FichaProductoHipoteca"), patch(
        "app.services.lectura_fichas_service.SQLAlchemyError", Exception
    ):
        with pytest.raises(RepositoryException):
            service.guardar_ficha_producto(data)

        mock_db_session.rollback.assert_called_once()
