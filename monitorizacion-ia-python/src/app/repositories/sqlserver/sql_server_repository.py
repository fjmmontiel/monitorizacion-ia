"""
Módulo para la interacción con bases de datos Microsoft SQL Server (MSSQL).

"""

from typing import TypeVar, Optional
from datetime import datetime

from qgdiag_lib_arquitectura.utilities.logging_conf import CustomLogger
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import declarative_base
from sqlalchemy import Integer, Float, Numeric, DateTime, String

from app.exceptions.app_exceptions import (
    RepositoryException,
    RepositoryIntegrityException,
)
from app.repositories.sqlserver.database_connector import get_manual_db_session
from app.models.model_session_dao import SesionSortAndFilterOptions


# Inicialización logger
logger = CustomLogger("sqlserver_repository")

# Tipado obj Base
Base = declarative_base()
T = TypeVar("T", bound=Base)


class SQLServerRepository:
    """
    Clase de repositorio para operaciones con bases de datos SQL Server.

    """

    def __init__(self):
        """
        Inicializa el repositorio con una sesión de base de datos de SQLAlchemy.
        """
        # init vacío intencionalmente, no se requiere lógica al crear la instancia
        pass

    def create_record(self, obj: T) -> T:
        """
        Crea un nuevo registro en la base de datos.

        Args:
            obj (T): El objeto SQLAlchemy a persistir en la base de datos.

        Raises:
            RepositoryIntegrityException: Si hay un conflicto de integridad (ej. ID duplicado).
            RepositoryException: Si ocurre un error inesperado durante el commit.

        Returns:
            T: El objeto persistido con sus valores actualizados (ej. IDs generados).
        """
        logger.debug(f"Intentando crear registro en tabla '{obj.__tablename__}'")

        try:
            db_session = get_manual_db_session()
            db_session.add(obj)
            db_session.commit()
            db_session.refresh(obj)
            logger.info(f"Registro guardado en '{obj.__tablename__}'")
            return obj
        except IntegrityError as e:
            db_session.rollback()
            logger.warning(f"Conflicto de integridad al crear registro: {str(e)}")
            raise RepositoryIntegrityException(
                f"El objeto ya existe o violación de integridad: {str(e)}"
            )
        except Exception as e:
            db_session.rollback()
            logger.error(
                f"Error inesperado al hacer commit en DB para el registro: {str(e)}"
            )
            raise RepositoryException(
                f"Error al hacer commit en DB para el registro: {str(e)}"
            )

        finally:
            db_session.close()

    def update_record(self, obj: T, db_session) -> T:
        """Actualiza un objeto existente."""
        try:
            db_session.commit()
            db_session.refresh(obj)
            return obj
        except IntegrityError as e:
            db_session.rollback()
            raise RepositoryIntegrityException(f"Error de integridad: {str(e)}")
        except Exception as e:
            db_session.rollback()
            raise RepositoryException(f"Error al actualizar: {str(e)}")

    def delete_record(self, obj: T, db_session) -> None:
        """Elimina un objeto."""
        try:
            db_session.delete(obj)
            db_session.commit()
        except Exception as e:
            db_session.rollback()
            raise RepositoryException(f"Error al eliminar: {str(e)}")

    def get_by_id(self, model: type[T], id_: str) -> T | None:
        """Obtiene un registro por ID."""
        try:
            db_session = get_manual_db_session()
            return (
                db_session.query(model)
                .filter(model.COD_ID_SESION_UNIQUE == id_)
                .first()
            )
        except Exception as e:
            raise RepositoryException(f"Error al obtener por ID: {str(e)}")
        finally:
            db_session.close()

    def get_filtered(
        self, model: type[T], options: SesionSortAndFilterOptions
    ) -> list[T] | None:
        """
        Obtiene registros de sesiones aplicando filtros, ordenación y paginación.
        """
        try:
            db_session = get_manual_db_session()
            query = db_session.query(model)

            # Aplicar filtros
            query = self._apply_filters(query, model, options.filtros)

            # Aplicar ordenación
            query = self._apply_ordering(
                query, model, options.campoOrden, options.direccionOrden
            )

            # Aplicar paginación
            query = self._apply_pagination(query, options.pagina, options.tamano)

            resultados = query.all()
            return resultados or None

        except Exception as e:
            logger.error(f"Error al obtener registros filtrados: {str(e)}")
            raise RepositoryException(f"Error al obtener registros filtrados: {str(e)}")
        finally:
            db_session.close()

    # -----------------------
    # Funciones auxiliares
    # -----------------------

    def _apply_filters(self, query, model, filtros):
        """Aplica filtros dinámicos a la query."""
        if not filtros:
            return query

        def _handle_ini(q, col, val):
            """Filtro dinámico"""
            dt = self._parse_iso_datetime(val)
            return q.filter(col >= dt) if dt else q

        def _handle_fin(q, col, val):
            """Filtro dinámico"""
            dt = self._parse_iso_datetime(val)
            return q.filter(col <= dt) if dt else q

        handlers = {
            "AUD_TIM_SESION_INI": _handle_ini,
            "AUD_TIM_SESION_FIN": _handle_fin,
        }

        for filtro in filtros:
            campo, valor = filtro.campo, filtro.valor
            if not campo or valor is None or not hasattr(model, campo):
                continue

            columna = getattr(model, campo)

            handler = handlers.get(campo)
            if handler:
                query = handler(query, columna, valor)
                continue

            col_type_name = type(columna.type).__name__
            if col_type_name == "String":
                query = query.filter(columna.like(f"%{valor}%"))
            else:
                coerced = self._coerce_value(columna, valor)
                query = query.filter(columna == coerced)

        return query

    def _apply_ordering(self, query, model, campo_orden, direccion):
        """Aplica ordenación si se especifica."""
        if campo_orden and hasattr(model, campo_orden):
            columna = getattr(model, campo_orden)
            if (direccion or "asc").lower() == "desc":
                return query.order_by(columna.desc())
            return query.order_by(columna.asc())
        return query

    def _apply_pagination(self, query, pagina, tamano):
        """Aplica paginación si se especifica."""
        if pagina and tamano and pagina > 0 and tamano > 0:
            offset = (pagina - 1) * tamano
            return query.offset(offset).limit(tamano)
        return query

    def _parse_iso_datetime(self, value: str) -> Optional[datetime]:
        """Convierte ISO 8601 a datetime; acepta 'Z' como UTC."""
        if value is None:
            return None
        try:
            # Soporte para 'Z' (UTC)
            v = value.strip()
            if v.endswith("Z"):
                v = v[:-1] + "+00:00"
            return datetime.fromisoformat(v)
        except Exception:
            logger.warning(f"No se pudo parsear fecha ISO: '{value}'")
            return None

    def _coerce_value(self, col, raw: str):
        """
        Intenta convertir el valor al tipo Python del campo.
        Si es string, devuelve el string tal cual.
        Si no puede determinar el tipo, devuelve el raw.
        """
        value = raw
        try:
            python_type = col.type.python_type
        except Exception:
            return raw

        try:
            if python_type is int:
                value = int(raw)
            if python_type is float:
                value = float(raw)
            if python_type is datetime:
                dt = self._parse_iso_datetime(raw)
                value = dt if dt is not None else raw
            # Para str u otros tipos, devolver tal cual
            value = raw
        except Exception:
            value = raw

        return value
