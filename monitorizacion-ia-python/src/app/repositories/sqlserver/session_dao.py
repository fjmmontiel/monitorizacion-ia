"""
Módulo que define el repositorio `SessionDAO` para gestionar operaciones CRUD sobre la tabla de sesiones
en una base de datos SQL Server. Proporciona métodos para insertar, actualizar, eliminar y recuperar
sesiones, aplicando filtros y transformando los datos al modelo de dominio `Session`.

Clases:
    SessionDAO: Implementa la lógica de acceso a datos para la entidad sesión.


"""

from app.managers.session_manager import Session


from app.exceptions.app_exceptions import (
    RepositoryException,
    RepositoryIntegrityException,
)
from app.models.model_session_dao import SessionModel
from app.repositories.sqlserver.sql_server_repository import SQLServerRepository
from qgdiag_lib_arquitectura.utilities.logging_conf import CustomLogger
from app.repositories.sqlserver.database_connector import get_manual_db_session
from app.models.model_session_dao import SesionSortAndFilterOptions


logger = CustomLogger("session_dao")


class SessionDAO(SQLServerRepository):
    """
    Repositorio específico para operaciones con la tabla de sesiones.
    """

    def __init__(self):
        # init vacío intencionalmente, no se requiere lógica al crear la instancia
        pass

    def insert_session(self, session: Session):
        """Inserta una nueva sesión en la base de datos"""
        session.actualizar()
        try:
            session_model = SessionModel(
                COD_ID_SESION_UNIQUE=session.session_id,
                NUM_INPUT_TOKENS=session.input_tokens,
                NUM_OUTPUT_TOKENS=session.output_tokens,
                POC_COSTE=session.cost,
                NUM_VALORACION=session.valoracion,
                DES_COMENTARIOS=session.comentarios,
                NUM_MUESTRA_INTERES=session.muestra_de_interes,
                NUM_SESION_DURACION=session.session_duration,
                AUD_TIM_SESION_INI=session.session_start,
                AUD_TIM_SESION_FIN=session.session_end,
                COD_CENTRO_SESION=session.centro,
                COD_GESTOR_SESION=session.gestor,
                DES_CONVERSACION=session.conversacion,
            )

            logger.debug(
                f"Insertando sesión con ID '{session_model.COD_ID_SESION_UNIQUE}'"
            )
            return self.create_record(session_model)
        except (RepositoryIntegrityException, RepositoryException):
            raise
        except Exception as e:
            logger.error(f"Error inesperado al insertar sesión: {str(e)}")
            raise RepositoryException(f"Error al insertar sesión: {str(e)}")

    def update_session(self, session: Session):
        """Actualiza una sesión existente"""
        session.actualizar()
        try:
            db_session = get_manual_db_session()
            session_model = (
                db_session.query(SessionModel)
                .filter(SessionModel.COD_ID_SESION_UNIQUE == session.session_id)
                .first()
            )
            if not session_model:
                logger.warning(f"Sesión '{session.session_id}' no encontrada.")
                return False

            session_model.NUM_INPUT_TOKENS = session.input_tokens
            session_model.NUM_OUTPUT_TOKENS = session.output_tokens
            session_model.POC_COSTE = session.cost
            session_model.NUM_VALORACION = session.valoracion
            session_model.DES_COMENTARIOS = session.comentarios
            session_model.NUM_MUESTRA_INTERES = session.muestra_de_interes
            session_model.NUM_SESION_DURACION = session.session_duration
            session_model.AUD_TIM_SESION_INI = session.session_start
            session_model.AUD_TIM_SESION_FIN = session.session_end
            session_model.COD_CENTRO_SESION = session.centro
            session_model.COD_GESTOR_SESION = session.gestor
            session_model.DES_CONVERSACION = session.conversacion

            return self.update_record(session_model, db_session)
        except Exception as e:
            logger.error(f"Error al actualizar sesión '{session.session_id}': {str(e)}")
            raise RepositoryException(f"Error al actualizar sesión: {str(e)}")
        finally:
            db_session.close()

    def delete_session(self, session_id: str):
        """Elimina una sesión por su ID"""
        try:
            db_session = get_manual_db_session()
            session_model = (
                db_session.query(SessionModel)
                .filter(SessionModel.COD_ID_SESION_UNIQUE == session_id)
                .first()
            )
            if not session_model:
                logger.warning(f"Sesión '{session_id}' no encontrada.")
                return False

            self.delete_record(session_model, db_session)
            logger.info(f"Sesión '{session_id}' eliminada correctamente.")
            return True
        except Exception as e:
            logger.error(f"Error al eliminar sesión '{session_id}': {str(e)}")
            raise RepositoryException(f"Error al eliminar sesión: {str(e)}")
        finally:
            db_session.close()

    def get_session(self, session_id: str) -> Session | None:
        """Recupera una sesión por su ID y la convierte a objeto de dominio (SessionManager.Session)"""
        try:
            session_model = self.get_by_id(SessionModel, session_id)
            return session_model.to_session() if session_model else None
        except Exception as e:
            logger.error(f"Error al recuperar sesión '{session_id}': {str(e)}")
            raise RepositoryException(f"Error al recuperar sesión: {str(e)}")

    def get_sessions(self, options: SesionSortAndFilterOptions) -> list[Session] | None:
        """
        Recupera las sesiones aplicando filtros y las convierte a objetos de dominio (Session).
        Args:
            options (SesionSortAndFilterOptions): Opciones de filtrado, ordenación y paginación.
        Returns:
            list[Session] | None: Lista de sesiones convertidas al modelo de dominio, o None si no hay resultados.
        """
        try:
            session_models = self.get_filtered(SessionModel, options)
            if not session_models:
                return None

            # Convertir cada SessionModel a Session usando su método to_session()
            sessions = [model.to_session() for model in session_models]
            return sessions

        except Exception as e:
            logger.error(f"Error al recuperar sesiones con filtros {options}: {str(e)}")
            raise RepositoryException(
                f"Error al recuperar sesiones con filtros {options}: {str(e)}"
            )
