"""
Repositorio para la gestión del contexto distribuido en base de datos
"""

from sqlalchemy import and_, desc
from typing import Optional, List, Dict, Any
import json
import uuid
from datetime import datetime

from app.models.model_data_session import DatosSesionTable
from app.managers.items import ContextItem
from app.managers.context import ToolCall
from sqlalchemy.exc import SQLAlchemyError

from app.repositories.sqlserver.database_connector import get_manual_db_session


class ContextRepository:
    """
    Repositorio para gestionar la persistencia del contexto en base de datos
    """

    def __init__(self):
        # init vacío inentaiconalmente, no se requiere lógica al crear la instancia
        pass

    def save_context_item(self, session_id: str, context_item: ContextItem) -> bool:
        """
        Guarda un ContextItem en la base de datos

        Args:
            session_id: ID de la sesión
            context_item: Item de contexto a guardar

        Returns:
            bool: True si se guardó correctamente
        """
        db_session = get_manual_db_session()
        try:
            # Verificar si ya existe este item para esta sesión
            existing_item = (
                db_session.query(DatosSesionTable)
                .filter(
                    and_(
                        DatosSesionTable.COD_ID_SESION_UNIQUE == session_id,
                        DatosSesionTable.COD_ID_DATO_UNIQUE == context_item.get_id(),
                    )
                )
                .first()
            )

            if existing_item:
                # Actualizar el item existente
                existing_item.DES_TIPO_DATO = context_item.item_type
                existing_item.DES_JSON = context_item.to_json()
                existing_item.AUD_TIM = datetime.now()
                existing_item.IND_DATO_VALIDO = True
            else:
                # Crear nuevo item
                nuevo_item = DatosSesionTable(
                    COD_ID_SESION_UNIQUE=session_id,
                    COD_ID_DATO_UNIQUE=context_item.get_id(),
                    DES_TIPO_DATO=context_item.item_type,
                    DES_JSON=context_item.to_json(),
                    AUD_TIM=datetime.now(),
                    IND_DATO_VALIDO=True,
                )
                db_session.add(nuevo_item)

            db_session.commit()
            return True

        except SQLAlchemyError as e:
            db_session.rollback()
            raise SQLAlchemyError(
                f"Error guardando context item {context_item.get_id()}: {str(e)}"
            )
        finally:
            db_session.close()

    def load_context_item(
        self, session_id: str, item_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Carga un ContextItem específico desde la base de datos

        Args:
            session_id: ID de la sesión
            item_id: ID del item a cargar

        Returns:
            Dict con los datos del item o None si no existe
        """
        db_session = get_manual_db_session()

        try:
            item = (
                db_session.query(DatosSesionTable)
                .filter(
                    and_(
                        DatosSesionTable.COD_ID_SESION_UNIQUE == session_id,
                        DatosSesionTable.COD_ID_DATO_UNIQUE == item_id,
                    )
                )
                .first()
            )

            if item:
                return {
                    "id": item.COD_ID_DATO_UNIQUE,
                    "type": item.DES_TIPO_DATO,
                    "data": json.loads(item.DES_JSON),
                    "timestamp": item.AUD_TIM,
                }
            return None

        except SQLAlchemyError as e:
            raise SQLAlchemyError(f"Error cargando context item {item_id}: {str(e)}")
        finally:
            db_session.close()

    def load_all_context_items(self, session_id: str) -> List[Dict[str, Any]]:
        """
        Carga todos los ContextItems de una sesión

        Args:
            session_id: ID de la sesión

        Returns:
            Lista de diccionarios con los datos de todos los items
        """
        db_session = get_manual_db_session()

        try:
            items = (
                db_session.query(DatosSesionTable)
                .filter(and_(DatosSesionTable.COD_ID_SESION_UNIQUE == session_id))
                .order_by(desc(DatosSesionTable.AUD_TIM))
                .all()
            )

            result = []
            for item in items:
                result.append(
                    {
                        "id": item.COD_ID_DATO_UNIQUE,
                        "type": item.DES_TIPO_DATO,
                        "data": json.loads(item.DES_JSON),
                        "timestamp": item.AUD_TIM,
                    }
                )

            return result

        except SQLAlchemyError as e:
            raise SQLAlchemyError(
                f"Error cargando context items para sesión {session_id}: {str(e)}"
            )
        finally:
            db_session.close()

    def delete_context_item(self, session_id: str, item_id: str) -> bool:
        """
        Marca un ContextItem como no válido (borrado lógico)

        Args:
            session_id: ID de la sesión
            item_id: ID del item a borrar

        Returns:
            bool: True si se borró correctamente
        """
        db_session = get_manual_db_session()
        try:
            item = (
                db_session.query(DatosSesionTable)
                .filter(
                    and_(
                        DatosSesionTable.COD_ID_SESION_UNIQUE == session_id,
                        DatosSesionTable.COD_ID_DATO_UNIQUE == item_id,
                    )
                )
                .first()
            )

            if item:
                db_session.delete(item)
                db_session.commit()
                return True
            return False

        except SQLAlchemyError as e:
            db_session.rollback()
            raise SQLAlchemyError(f"Error borrando context item {item_id}: {str(e)}")
        finally:
            db_session.close()

    def save_tool_call_log(self, session_id: str, tool_call: ToolCall) -> bool:
        """
        Guarda una llamada a herramienta en la base de datos

        Args:
            session_id: ID de la sesión
            tool_call: Llamada a herramienta a guardar

        Returns:
            bool: True si se guardó correctamente
        """
        db_session = get_manual_db_session()

        try:
            # Generar un ID único para esta tool call
            tool_call_id = f"tool_call_{uuid.uuid4().hex[:8]}"

            tool_call_data = DatosSesionTable(
                COD_ID_SESION_UNIQUE=session_id,
                COD_ID_DATO_UNIQUE=tool_call_id,
                DES_TIPO_DATO="tool_call",
                DES_JSON=tool_call.json(),
                AUD_TIM=datetime.now(),
                IND_DATO_VALIDO=True,
            )

            db_session.add(tool_call_data)
            db_session.commit()
            return True

        except SQLAlchemyError as e:
            db_session.rollback()
            raise SQLAlchemyError(f"Error guardando tool call: {str(e)}")
        finally:
            db_session.close()

    def load_tool_call_log(self, session_id: str) -> List[Dict[str, Any]]:
        """
        Carga todas las llamadas a herramientas de una sesión

        Args:
            session_id: ID de la sesión

        Returns:
            Lista de tool calls
        """
        db_session = get_manual_db_session()

        try:
            tool_calls = (
                db_session.query(DatosSesionTable)
                .filter(
                    and_(
                        DatosSesionTable.COD_ID_SESION_UNIQUE == session_id,
                        DatosSesionTable.DES_TIPO_DATO == "tool_call",
                        DatosSesionTable.IND_DATO_VALIDO == True,
                    )
                )
                .order_by(DatosSesionTable.AUD_TIM)
                .all()
            )

            result = []
            for tool_call in tool_calls:
                result.append(json.loads(tool_call.DES_JSON))

            return result

        except SQLAlchemyError as e:
            raise SQLAlchemyError(
                f"Error cargando tool call log para sesión {session_id}: {str(e)}"
            )
        finally:
            db_session.close()

    def clear_session_context(self, session_id: str) -> bool:
        """
        Limpia todo el contexto de una sesión (borrado lógico)

        Args:
            session_id: ID de la sesión

        Returns:
            bool: True si se limpió correctamente
        """
        db_session = get_manual_db_session()

        try:
            items = (
                db_session.query(DatosSesionTable)
                .filter(DatosSesionTable.COD_ID_SESION_UNIQUE == session_id)
                .all()
            )

            for item in items:
                item.IND_DATO_VALIDO = False
                item.AUD_TIM = datetime.now()

            db_session.commit()
            return True

        except SQLAlchemyError as e:
            db_session.rollback()
            raise SQLAlchemyError(
                f"Error limpiando contexto de sesión {session_id}: {str(e)}"
            )
        finally:
            db_session.close()
