"""
Test unitarios para LecturaTraduccionesService.

Incluye pruebas de:
- Lectura y procesamiento de archivos CSV.
- Exclusión de archivos específicos.
.- Inserción/actualización de traducciones en base de datos.
- Manejo de errores en persistencia.

Se utilizan fixtures y mocks para simular la sesión de base de datos y archivos.
"""

import json
import pandas as pd
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch
from sqlalchemy.exc import SQLAlchemyError

from app.services.lectura_fichas_service import LecturaTraduccionesService
from app.exceptions.app_exceptions import RepositoryException


@pytest.fixture
def mock_db_session():
    """Mock de la sesión de base de datos SQLAlchemy."""
    session = MagicMock()
    return session


def test_procesar_fichas_ignora_archivo_excluido(tmp_path: Path, mock_db_session):
    """Verifica que los archivos excluidos por nombre son ignorados al procesar fichas."""
    # Crear un CSV con el nombre que debe excluirse
    excluido = tmp_path / "IAG_MVP_SEGURO_20250926.csv"
    excluido.write_text("col1\tcol2\nx\ty\n", encoding="utf-8")

    service = LecturaTraduccionesService(tmp_path, mock_db_session)

    df = service.procesar_fichas()

    # Debe devolver DataFrame vacío
    assert df.empty


def test_guardar_traducciones_inserta_y_commit(mock_db_session):
    """Comprueba que guardar_traducciones llama a merge y commit correctamente."""
    # Crear un DataFrame simulado
    data = {
        "DES_NOMBRE_FICHERO": ["fichero.csv"],
        "DES_TIPO_DATO": ["fichero"],
        "DES_COMPLETA": ['[{"col1": "valor"}]'],
    }
    df = pd.DataFrame(data)

    service = LecturaTraduccionesService("dummy_path", mock_db_session)

    # Ejecutar guardar_traducciones
    service.guardar_traducciones(df)

    # Debe haberse llamado a merge y a commit
    assert mock_db_session.merge.called
    assert mock_db_session.commit.called


def test_guardar_traducciones_error(mock_db_session):
    """Simula un error en merge y verifica que se ejecuta rollback y se lanza excepción."""
    # Configurar para que falle merge
    mock_db_session.merge.side_effect = SQLAlchemyError("DB error")

    data = {
        "DES_NOMBRE_FICHERO": ["fichero.csv"],
        "DES_TIPO_DATO": ["fichero"],
        "DES_COMPLETA": ['[{"col1": "valor"}]'],
    }
    df = pd.DataFrame(data)

    service = LecturaTraduccionesService("dummy_path", mock_db_session)

    with pytest.raises(RepositoryException) as exc_info:
        service.guardar_traducciones(df)

    # Debe haberse hecho rollback
    assert mock_db_session.rollback.called
    assert "DB error" in str(exc_info.value)


def test_procesar_fichas_unicode_decodeerror(tmp_path, mock_db_session):
    """Test"""
    csv_file = tmp_path / "bad_encoding.csv"
    csv_file.write_text("col1\tcol2\nvalor1\tvalor2\n", encoding="latin1")

    service = LecturaTraduccionesService(tmp_path, mock_db_session)

    with patch(
        "pandas.read_csv",
        side_effect=[
            UnicodeDecodeError("utf-8", b"", 0, 1, "reason"),
            pd.DataFrame([{"col1": "ok"}]),
        ],
    ):
        df = service.procesar_fichas()

    assert not df.empty
    assert "DES_COMPLETA" in df.columns
    assert "ok" in df.iloc[0]["DES_COMPLETA"]


def test_procesar_fichas_runtime_error(tmp_path, mock_db_session):
    """Test"""
    csv_file = tmp_path / "corrupt.csv"
    csv_file.write_text("dummy", encoding="utf-8")

    service = LecturaTraduccionesService(tmp_path, mock_db_session)

    with patch("pandas.read_csv", side_effect=Exception("Boom!")):
        with pytest.raises(RuntimeError) as exc_info:
            service.procesar_fichas()

    assert "corrupt.csv" in str(exc_info.value)
