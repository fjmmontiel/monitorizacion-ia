"""
Tests para el módulo de conexión a base de datos.

Este conjunto de pruebas valida las funciones `get_db_session` y
`get_manual_db_session`, asegurando que manejan correctamente la configuración
de la base de datos, los errores de parámetros faltantes y la creación/cierre
de sesiones.
"""

import pytest
from unittest.mock import patch, MagicMock

from app.exceptions.app_exceptions import RepositoryException
from app.repositories.sqlserver import database_connector


class TestDatabaseConnector:
    """
    Pruebas unitarias para las funciones de conexión a base de datos
    definidas en `database_connector`.
    """

    @pytest.fixture
    def mock_settings(self, monkeypatch):
        """Fixture para simular configuración válida de base de datos MSSQL."""
        monkeypatch.setattr(
            database_connector.settings, "DATABASE_SERVER_TYPE", "mssql"
        )
        monkeypatch.setattr(database_connector.settings, "DATABASE_USER", "user")
        monkeypatch.setattr(database_connector.settings, "DATABASE_PASSWORD", "pass")
        monkeypatch.setattr(database_connector.settings, "DATABASE_HOST", "localhost")
        monkeypatch.setattr(database_connector.settings, "DATABASE_NAME", "testdb")
        monkeypatch.setattr(database_connector.settings, "DATABASE_PORT", 1433)
        monkeypatch.setattr(
            database_connector.settings,
            "DATABASE_DRIVER",
            "ODBC Driver 17 for SQL Server",
        )
        monkeypatch.setattr(database_connector.settings, "DATABASE_ENCRYPT", True)
        monkeypatch.setattr(
            database_connector.settings, "DATABASE_TRUST_SERVER_CERTIFICATE", True
        )
        monkeypatch.setattr(
            database_connector.settings, "DATABASE_DRIVER_TYPE", "pyodbc"
        )
        return database_connector.settings

    def test_get_db_session_success(self, mock_settings):
        """Debe crear y cerrar una sesión correctamente usando get_db_session."""
        fake_session = MagicMock()
        with patch.object(
            database_connector._db_handler_instance,
            "create_connection",
            return_value=fake_session,
        ):
            gen = database_connector.get_db_session()
            session = next(gen)
            assert session is fake_session
            # Forzar cierre
            gen.close()
            fake_session.close.assert_called_once()

    def test_get_db_session_incomplete_settings(self, monkeypatch):
        """Debe lanzar RepositoryException si faltan parámetros críticos."""
        monkeypatch.setattr(
            database_connector.settings, "DATABASE_SERVER_TYPE", "mssql"
        )
        monkeypatch.setattr(database_connector.settings, "DATABASE_USER", None)
        monkeypatch.setattr(database_connector.settings, "DATABASE_PASSWORD", "pass")
        monkeypatch.setattr(database_connector.settings, "DATABASE_HOST", "localhost")
        monkeypatch.setattr(database_connector.settings, "DATABASE_NAME", "testdb")

        with pytest.raises(
            RepositoryException, match="Configuración de base de datos incompleta"
        ):
            next(database_connector.get_db_session())

    def test_get_db_session_wrong_type(self, monkeypatch):
        """Debe lanzar RepositoryException si el tipo de servidor no es MSSQL."""
        monkeypatch.setattr(
            database_connector.settings, "DATABASE_SERVER_TYPE", "postgres"
        )
        with pytest.raises(RepositoryException, match="DATABASE_TYPE 'postgres'"):
            next(database_connector.get_db_session())

    def test_get_db_session_none_connection(self, mock_settings):
        """Debe lanzar RepositoryException si create_connection devuelve None."""
        with patch.object(
            database_connector._db_handler_instance,
            "create_connection",
            return_value=None,
        ):
            with pytest.raises(RepositoryException, match="No se pudo crear la sesión"):
                next(database_connector.get_db_session())

    def test_get_manual_db_session_success(self, mock_settings):
        """Debe devolver una sesión válida usando get_manual_db_session."""
        fake_session = MagicMock()
        with patch.object(
            database_connector._db_handler_instance,
            "create_connection",
            return_value=fake_session,
        ):
            session = database_connector.get_manual_db_session()
            assert session is fake_session

    def test_get_manual_db_session_incomplete_settings(self, monkeypatch):
        """Debe lanzar RepositoryException si faltan parámetros críticos en get_manual_db_session."""
        monkeypatch.setattr(
            database_connector.settings, "DATABASE_SERVER_TYPE", "mssql"
        )
        monkeypatch.setattr(database_connector.settings, "DATABASE_USER", None)
        monkeypatch.setattr(database_connector.settings, "DATABASE_PASSWORD", "pass")
        monkeypatch.setattr(database_connector.settings, "DATABASE_HOST", "localhost")
        monkeypatch.setattr(database_connector.settings, "DATABASE_NAME", "testdb")

        with pytest.raises(
            RepositoryException, match="Configuración de base de datos incompleta"
        ):
            database_connector.get_manual_db_session()

    def test_get_manual_db_session_wrong_type(self, monkeypatch):
        """Debe lanzar RepositoryException si el tipo de servidor no es MSSQL en get_manual_db_session."""
        monkeypatch.setattr(
            database_connector.settings, "DATABASE_SERVER_TYPE", "oracle"
        )
        with pytest.raises(RepositoryException, match="DATABASE_TYPE 'oracle'"):
            database_connector.get_manual_db_session()

    def test_get_manual_db_session_none_connection(self, mock_settings):
        """Debe lanzar RepositoryException si create_connection devuelve None en get_manual_db_session."""
        with patch.object(
            database_connector._db_handler_instance,
            "create_connection",
            return_value=None,
        ):
            with pytest.raises(RepositoryException, match="No se pudo crear la sesión"):
                database_connector.get_manual_db_session()
