"""Excepciones de la aplicacion"""

from typing import Any

from fastapi import HTTPException, status


# GENERAL
class ResourceNotFoundException(HTTPException):

    """Excepción lanzada cuando un recurso no es encontrado."""

    def __init__(self, message: str = "Recurso no encontrado."):
        super().__init__(detail = message, status_code=status.HTTP_404_NOT_FOUND)


class ServiceException(HTTPException):
    """Excepción base para errores en la capa de servicio."""

    def __init__(self, detail: str = "Error en el servicio.", status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR):
        super().__init__(detail = detail, status_code=status_code)


# REPOSITORY
class RepositoryException(HTTPException):
    """Exception for repository error"""

    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail
        )


class RepositoryIntegrityException(HTTPException):
    """Exception for repository error"""

    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail
        )


class RepositoryResourceNotFoudException(HTTPException):
    """Exception for repository error"""

    def __init__(self, detail: str):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


# TASK EXCEPTION
class TaskException(Exception):
    """Exception for task error"""

    def __init__(self, detail: str):
        super().__init__(detail)


class FileProcessingException(HTTPException):
    """
    Base exception for file processing errors.
    """

    def __init__(
        self, detail: str, status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    ):
        super().__init__(status_code=status_code, detail=detail)


class FileWriteError(FileProcessingException):
    """
    Raised when there's an error writing a file to disk.
    """

    def __init__(self, detail: str = "Error writing file(s) to storage."):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail
        )


class FileReadError(FileProcessingException):
    """
    Raised when there's an error reading a file to disk.
    """

    def __init__(self, detail: str = "Error reading file(s) to storage."):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail
        )


# REST CLIENT EXCEPTIONS
class RestClientError(ServiceException):
    """Excepción base para errores en cualquier RestClient."""
    
    def __init__(self, message: str = "Rest client error."):
            super().__init__(detail=message, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RestClientHttpError(RestClientError):
    """
    Excepción lanzada para respuestas HTTP con códigos de error (4xx).
    """

    def __init__(self, message: str, status_code: int, response_content: Any = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_content = response_content


class RestClientServerError(RestClientHttpError):
    """Error HTTP 5xx."""

    def __init__(
        self,
        message: str = "Error interno del servicio externo.",
        response_content: Any = None,
    ):
        super().__init__(message, status_code=500, response_content=response_content)