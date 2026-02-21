from enum import StrEnum

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel


class ErrorCode(StrEnum):
    UNKNOWN_USE_CASE = 'UNKNOWN_USE_CASE'
    VALIDATION_ERROR = 'VALIDATION_ERROR'
    UPSTREAM_ERROR = 'UPSTREAM_ERROR'
    UPSTREAM_TIMEOUT = 'UPSTREAM_TIMEOUT'
    INTERNAL_ERROR = 'INTERNAL_ERROR'


class ErrorResponse(BaseModel):
    schema_version: str = 'v1'
    code: ErrorCode
    message: str
    detail: dict | None = None


class OrchestratorError(Exception):
    def __init__(self, code: ErrorCode, message: str, status_code: int, detail: dict | None = None):
        self.code = code
        self.message = message
        self.status_code = status_code
        self.detail = detail
        super().__init__(message)


def install_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(OrchestratorError)
    async def handle_orch_error(_: Request, exc: OrchestratorError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse(code=exc.code, message=exc.message, detail=exc.detail).model_dump(),
        )

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(_: Request, exc: RequestValidationError) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content=ErrorResponse(
                code=ErrorCode.VALIDATION_ERROR,
                message='Validation failed',
                detail={'errors': exc.errors()},
            ).model_dump(),
        )

    @app.exception_handler(Exception)
    async def handle_unexpected_error(_: Request, exc: Exception) -> JSONResponse:
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(
                code=ErrorCode.INTERNAL_ERROR,
                message='Internal server error',
                detail={'error_type': type(exc).__name__},
            ).model_dump(),
        )
