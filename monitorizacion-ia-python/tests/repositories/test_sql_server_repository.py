"""Tests para tools_recomendacion_hipoteca."""

import pytest
from unittest.mock import MagicMock, patch
from sqlalchemy.exc import IntegrityError

from app.repositories.sqlserver.session_dao import SessionDAO
from app.exceptions.app_exceptions import (
    RepositoryIntegrityException,
    RepositoryException,
)


# Dummy modelo para pruebas
class DummyModel:
    """Clase para tests"""

    COD_ID_SESION_UNIQUE = "123"
    __tablename__ = "dummy_table"


@pytest.fixture
def dao():
    """DAO que usará SessionDAO"""
    return SessionDAO()


@pytest.fixture
def fake_session():
    """Tests para tools_recomendacion_hipoteca."""
    return MagicMock()


def patch_db_session(fake_session):
    """Tests para tools_recomendacion_hipoteca."""
    return patch(
        "app.repositories.sqlserver.sql_server_repository.get_manual_db_session",
        return_value=fake_session,
    )


def test_create_record_success(dao, fake_session):
    """Tests para tools_recomendacion_hipoteca."""
    obj = DummyModel()
    with patch_db_session(fake_session):
        result = dao.create_record(obj)
        fake_session.add.assert_called_once_with(obj)
        fake_session.commit.assert_called_once()
        fake_session.refresh.assert_called_once_with(obj)
        assert result == obj


def test_create_record_integrity_error(dao, fake_session):
    """Tests para tools_recomendacion_hipoteca."""
    obj = DummyModel()
    fake_session.commit.side_effect = IntegrityError("msg", "params", "orig")
    with patch_db_session(fake_session):
        with pytest.raises(RepositoryIntegrityException):
            dao.create_record(obj)
        fake_session.rollback.assert_called_once()


def test_create_record_generic_exception(dao, fake_session):
    """Tests para tools_recomendacion_hipoteca."""
    obj = DummyModel()
    fake_session.commit.side_effect = Exception("fail")
    with patch_db_session(fake_session):
        with pytest.raises(RepositoryException):
            dao.create_record(obj)
        fake_session.rollback.assert_called_once()


def test_update_record_success(dao, fake_session):
    """Tests para tools_recomendacion_hipoteca."""
    obj = DummyModel()
    with patch_db_session(fake_session):
        result = dao.update_record(obj, fake_session)
        fake_session.commit.assert_called_once()
        fake_session.refresh.assert_called_once_with(obj)
        assert result == obj


def test_update_record_integrity_error(dao, fake_session):
    """Tests para tools_recomendacion_hipoteca."""
    obj = DummyModel()
    fake_session.commit.side_effect = IntegrityError("msg", "params", "orig")
    with patch_db_session(fake_session):
        with pytest.raises(RepositoryIntegrityException):
            dao.update_record(obj, fake_session)
        fake_session.rollback.assert_called_once()


def test_update_record_generic_exception(dao, fake_session):
    """Tests para tools_recomendacion_hipoteca."""
    obj = DummyModel()
    fake_session.commit.side_effect = Exception("fail")
    with patch_db_session(fake_session):
        with pytest.raises(RepositoryException):
            dao.update_record(obj, fake_session)
        fake_session.rollback.assert_called_once()


def test_delete_record_success(dao, fake_session):
    """Tests para tools_recomendacion_hipoteca."""
    obj = DummyModel()
    with patch_db_session(fake_session):
        result = dao.delete_record(obj, fake_session)
        fake_session.delete.assert_called_once_with(obj)
        fake_session.commit.assert_called_once()


def test_delete_record_exception(dao, fake_session):
    """Tests para tools_recomendacion_hipoteca."""
    obj = DummyModel()
    fake_session.delete.side_effect = Exception("fail")
    with patch_db_session(fake_session):
        with pytest.raises(RepositoryException):
            dao.delete_record(obj, fake_session)
        fake_session.rollback.assert_called_once()


def test_get_by_id_success(dao, fake_session):
    """Tests para tools_recomendacion_hipoteca."""
    dummy_instance = DummyModel()
    fake_session.query.return_value.filter.return_value.first.return_value = (
        dummy_instance
    )
    with patch_db_session(fake_session):
        result = dao.get_by_id(DummyModel, "123")
        fake_session.query.assert_called_once_with(DummyModel)
        assert result == dummy_instance


def test_get_by_id_exception(dao, fake_session):
    """Tests para tools_recomendacion_hipoteca."""
    fake_session.query.side_effect = Exception("fail")
    with patch_db_session(fake_session):
        with pytest.raises(RepositoryException):
            dao.get_by_id(DummyModel, "123")
