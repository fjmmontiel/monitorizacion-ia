""" Modulo"""

import pytest
from fastapi import status, HTTPException
from app.exceptions.app_exceptions import (
    ResourceNotFoundException,
    RepositoryResourceNotFoudException,
    ServiceException,
    RepositoryException,
    RepositoryIntegrityException,
    TaskException,
    FileProcessingException,
    FileWriteError,
    FileReadError,
    RestClientError,
    RestClientHttpError,
    RestClientServerError,
)

# GENERAL
def test_resource_not_found_exception_default_message():
    """ Modulo"""
    exc = ResourceNotFoundException()
    assert isinstance(exc, ResourceNotFoundException)
    assert exc.detail == "Recurso no encontrado."

def test_service_exception_custom_message():
    """ Modulo"""
    exc = ServiceException("custom service error")
    assert exc.detail == "custom service error"

# REPOSITORY
def test_repository_exception_sets_status_and_detail():
    """ Modulo"""
    exc = RepositoryException("db error")
    assert exc.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert exc.detail == "db error"

def test_repository_integrity_exception():
    """ Modulo"""
    exc = RepositoryIntegrityException("integrity issue")
    assert exc.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert exc.detail == "integrity issue"

def test_resource_not_found_repository_version():
    """ Modulo"""
    exc = RepositoryResourceNotFoudException("not found repo")
    assert exc.status_code == status.HTTP_404_NOT_FOUND
    assert exc.detail == "not found repo"

# TASK
def test_task_exception_raises():
    """ Modulo"""
    with pytest.raises(TaskException, match="task failed"):
        raise TaskException("task failed")

# FILE PROCESSING
def test_file_processing_exception_base():
    """ Modulo"""
    exc = FileProcessingException("file processing error")
    assert exc.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert exc.detail == "file processing error"

def test_file_write_error_defaults():
    """ Modulo"""
    exc = FileWriteError()
    assert exc.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "writing file" in exc.detail

def test_file_read_error_defaults():
    """ Modulo"""
    exc = FileReadError()
    assert exc.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "reading file" in exc.detail

# REST CLIENT
def test_rest_client_error_inheritance():
    """ Modulo"""
    exc = RestClientError("rest client error")
    # Herencia
    assert isinstance(exc, RestClientError)
    assert isinstance(exc, ServiceException)
    # VALORES
    assert exc.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert exc.detail == "rest client error"

def test_rest_client_http_error_sets_attrs():
    """ Modulo"""
    exc = RestClientHttpError("bad request", status_code=400, response_content={"error": "bad"})
    assert exc.detail == "bad request"
    assert exc.status_code == 400
    assert exc.response_content == {"error": "bad"}

def test_rest_client_server_error_defaults():
    """ Modulo"""
    exc = RestClientServerError()
    assert exc.status_code == 500
    assert "servicio externo" in exc.detail
    assert exc.response_content is None
