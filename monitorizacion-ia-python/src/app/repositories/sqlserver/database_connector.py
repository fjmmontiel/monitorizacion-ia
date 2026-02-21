"""Modulo de inicializacion y gestion de sesiones de base de datos"""

from typing import Iterator

from qgdiag_lib_arquitectura.data.sql_database import SQLDatabase
from sqlalchemy.orm import Session as SQLAlchemySession

from app.exceptions.app_exceptions import RepositoryException
from app.settings import settings

_db_handler_instance = SQLDatabase()


def get_db_session() -> Iterator[SQLAlchemySession]:
    """
    Inicia una sesión en base de datos.
    """

    if (
        settings.DATABASE_SERVER_TYPE
        and settings.DATABASE_SERVER_TYPE.lower() == "mssql"
    ):
        required_settings = [
            settings.DATABASE_USER,
            settings.DATABASE_PASSWORD,
            settings.DATABASE_HOST,
            settings.DATABASE_NAME,
        ]
        if not all(required_settings):
            missing = [
                name
                for name, value in zip(
                    [
                        "DATABASE_USER",
                        "DATABASE_PASSWORD",
                        "DATABASE_SERVER",
                        "DATABASE_NAME",
                    ],
                    required_settings,
                )
                if not value
            ]
            raise RepositoryException(
                "Configuración de base de datos incompleta. "
                f"Faltan parámetros críticos: {', SQLSERVER_'.join(missing)}."
            )

        db_session_instance = _db_handler_instance.create_connection(
            username=settings.DATABASE_USER,
            password=settings.DATABASE_PASSWORD,
            host=settings.DATABASE_HOST,
            port=settings.DATABASE_PORT,
            database_name=settings.DATABASE_NAME,
            driver=settings.DATABASE_DRIVER,
            encrypt=settings.DATABASE_ENCRYPT,
            trust_server_certificate=settings.DATABASE_TRUST_SERVER_CERTIFICATE,
            server_type=settings.DATABASE_SERVER_TYPE,
            driver_type=settings.DATABASE_DRIVER_TYPE,
        )
    else:
        raise RepositoryException(
            f"DATABASE_TYPE '{settings.DATABASE_SERVER_TYPE}'"
            "no está configurado como 'mssql' o no es soportado."
            "Verifica la variable DATABASE_SERVER_TYPE en tu .env y config.py."
        )

    if db_session_instance is None:  # Salvaguarda
        raise RepositoryException(
            "No se pudo crear la sesión de base de datos."
            "_db_handler_instance.create_connection devolvió None."
        )

    try:
        yield db_session_instance
    finally:
        if db_session_instance is not None:
            db_session_instance.close()




def get_manual_db_session() -> SQLAlchemySession:
    """
    Crea e inicializa una sesión de base de datos de forma directa (sin yield).
    Útil para usar fuera de los endpoints, por ejemplo en agentes.
    """
    if (
        settings.DATABASE_SERVER_TYPE
        and settings.DATABASE_SERVER_TYPE.lower() == "mssql"
    ):
        required_settings = [
            settings.DATABASE_USER,
            settings.DATABASE_PASSWORD,
            settings.DATABASE_HOST,
            settings.DATABASE_NAME,
        ]
        if not all(required_settings):
            missing = [
                name
                for name, value in zip(
                    [
                        "DATABASE_USER",
                        "DATABASE_PASSWORD",
                        "DATABASE_SERVER",
                        "DATABASE_NAME",
                    ],
                    required_settings,
                )
                if not value
            ]
            raise RepositoryException(
                "Configuración de base de datos incompleta. "
                f"Faltan parámetros críticos: {', SQLSERVER_'.join(missing)}."
            )

        db_session_instance = _db_handler_instance.create_connection(
            username=settings.DATABASE_USER,
            password=settings.DATABASE_PASSWORD,
            host=settings.DATABASE_HOST,
            port=settings.DATABASE_PORT,
            database_name=settings.DATABASE_NAME,
            driver=settings.DATABASE_DRIVER,
            encrypt=settings.DATABASE_ENCRYPT,
            trust_server_certificate=settings.DATABASE_TRUST_SERVER_CERTIFICATE,
            server_type=settings.DATABASE_SERVER_TYPE,
            driver_type=settings.DATABASE_DRIVER_TYPE,
        )
    else:
        raise RepositoryException(
            f"DATABASE_TYPE '{settings.DATABASE_SERVER_TYPE}'"
            " no está configurado como 'mssql' o no es soportado."
            " Verifica la variable DATABASE_SERVER_TYPE en tu .env y config.py."
        )

    if db_session_instance is None:
        raise RepositoryException("No se pudo crear la sesión de base de datos.")
    
    return db_session_instance
