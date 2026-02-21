"""
Gestión distribuida de contexto con persistencia en base de datos.

Este módulo proporciona una implementación distribuida del sistema de contexto que
permite la persistencia y recuperación de información contextual en base de datos.
Reemplaza la funcionalidad singleton legacy con un enfoque distribuido apropiado
para entornos multi-sesión.

Classes:
    - DistributedContext: Contexto distribuido con persistencia en BD
    - DistributedSessionManager: Gestor de sesiones distribuidas

Features:
    - Persistencia automática de elementos de contexto en base de datos
    - Gestión de métricas de sesión (tokens, costes)
    - Reconstrucción de contexto desde datos persistidos
    - Gestión de múltiples sesiones concurrentes
    - Integración con managers de observadores

Note:
    Esta implementación reemplaza SessionSingleton para proporcionar
    funcionalidad distribuida y escalable en el sistema de hipotecas.
"""

from typing import Dict, Any, Optional

from app.managers.context import Context, ToolCall, ToolCallLog
from app.managers.items import ContextItem
from app.managers.session_manager import Session
from app.repositories.context_repository import ContextRepository
from app.repositories.sqlserver.session_dao import SessionDAO
from sqlalchemy.exc import SQLAlchemyError
from qgdiag_lib_arquitectura import CustomLogger

logger = CustomLogger("Contexto distribuido.")


class DistributedContext(Context):
    """
    Implementación distribuida del contexto que persiste en base de datos
    """

    def __init__(self, session_id: str, headers: dict):
        """
        Inicializa el contexto distribuido

        Args:
            session_id: ID de la sesión
        """
        super().__init__()
        self.session_id = session_id
        self.headers = headers
        self.repository = ContextRepository()
        self._loaded = False

        # Gestión de la sesión para métricas (tokens, costes, etc.)
        self.session_dao = SessionDAO()
        self.session_metrics = None
        # Nos aseguramos de que el contexto se lee de base de datos
        self._ensure_loaded()

    def _ensure_loaded(self):
        """
        Asegura que el contexto está cargado desde la base de datos
        """
        if not self._loaded:
            self._load_from_database()
            self._loaded = True

    def _load_from_database(self):
        """
        Carga el contexto completo desde la base de datos
        """
        try:
            # Cargar session metrics
            self.session_metrics = self.session_dao.get_session(self.session_id)

            # Cargar items de contexto
            db_items = self.repository.load_all_context_items(self.session_id)
            self.items = {}

            for db_item in db_items:
                # Aquí necesitaremos un factory para reconstruir los ContextItems
                # desde los datos JSON guardados
                context_item = self._reconstruct_context_item(db_item)
                if context_item:
                    self.items[context_item.get_id()] = context_item

            # Cargar tool call log
            tool_calls_data = self.repository.load_tool_call_log(self.session_id)
            self.tool_call_log = ToolCallLog()

            for tool_call_data in tool_calls_data:
                tool_call = ToolCall(**tool_call_data)
                self.tool_call_log.add(tool_call)

        except Exception as e:
            logger.info(f"Error cargando contexto desde BD: {str(e)}")
            # Si hay error, mantenemos el contexto vacío

    def _reconstruct_context_item(
        self, db_item: Dict[str, Any]
    ) -> Optional[ContextItem]:
        """
        Reconstruye un ContextItem desde los datos de la base de datos

        Args:
            db_item: Datos del item desde la BD

        Returns:
            ContextItem reconstruido o None si hay error
        """
        try:
            # Importamos dinámicamente las clases de items basándose en el tipo
            item_type = db_item["type"]
            item_data = db_item["data"]

            # Aquí necesitaremos mapear tipos a clases
            # Por ahora, intentamos reconstruir genéricamente
            from app.managers.items import (
                EzDataCliente,
                EzDataGestor,
                EzRecomendacionHipoteca,
                EzDataPreeval,
                EzDataOperacion,
                EzDataInterviniente,
                EzDataMuestraInteres,
            )

            type_mapping = {
                "DataCliente": EzDataCliente,
                "DataGestor": EzDataGestor,
                "RecomendacionHipoteca": EzRecomendacionHipoteca,
                "DataPreeval": EzDataPreeval,
                "DataOperacion": EzDataOperacion,
                "DataInterviniente": EzDataInterviniente,
                "DataMuestraInteres": EzDataMuestraInteres,
            }

            if item_type in type_mapping:
                # Reconstruir el item usando los datos JSON
                item_class = type_mapping[item_type]
                # Crear una instancia básica y luego restaurar los datos
                item = item_class.__new__(item_class)
                item.__dict__.update(item_data)
                return item

            return None

        except Exception as e:
            return None

    def _put_item(self, item: ContextItem) -> None:
        """
        Sobrescribe el método para persistir en BD
        """
        self._ensure_loaded()

        # Persistir en base de datos
        try:
            self.repository.save_context_item(self.session_id, item)
            super()._put_item(item)
        except Exception as e:
            msg_error = f"Error persistiendo item {item.get_id()}: {str(e)}"
            logger.info(msg_error)
            raise SQLAlchemyError(msg_error)

    def _remove_item(self, item: ContextItem) -> None:
        """
        Sobrescribe el método para actualizar BD
        """
        self._ensure_loaded()
        super()._remove_item(item)

        # Actualizar en base de datos
        try:
            self.repository.delete_context_item(self.session_id, item.get_id())
        except Exception as e:
            logger.info(f"Error eliminando item {item.get_id()}: {str(e)}")

    def get_item(self, id: str) -> ContextItem:
        """
        Sobrescribe el método para asegurar carga desde BD
        """
        self._ensure_loaded()
        return super().get_item(id)

    def add_tool_call(self, tool_call: ToolCall) -> None:
        """
        Sobrescribe el método para persistir tool calls
        """
        self._ensure_loaded()
        super().add_tool_call(tool_call)

        # Persistir en base de datos
        try:
            self.repository.save_tool_call_log(self.session_id, tool_call)
        except Exception as e:
            logger.info(f"Error persistiendo tool call: {str(e)}")

    def get_llm_str(self) -> str:
        """
        Sobrescribe para asegurar carga desde BD
        """
        self._ensure_loaded()
        return super().get_llm_str()

    def to_json(self):
        """
        Sobrescribe para asegurar carga desde BD
        """
        self._ensure_loaded()
        return super().to_json()

    def clear_context(self):
        """
        Limpia todo el contexto tanto en memoria como en BD
        """
        self.items = {}
        self.tool_call_log = ToolCallLog()
        self.conversation_outputs = []

        # Limpiar en base de datos
        try:
            self.repository.clear_session_context(self.session_id)
        except Exception as e:
            logger.info(f"Error limpiando contexto en BD: {str(e)}")

    def save_session_metrics(self):
        """
        Guarda las métricas de la sesión en base de datos
        """
        try:
            self.session_metrics.actualizar()

            # Verificar si ya existe la sesión en BD
            existing_session = self.session_dao.get_session(self.session_id)
            if existing_session:
                self.session_dao.update_session(self.session_metrics)
            else:
                self.session_dao.insert_session(self.session_metrics)
        except Exception as e:
            logger.info(f"Error guardando métricas de sesión: {str(e)}")

    def get_session_metrics(self) -> Session:
        """
        Obtiene las métricas de la sesión actual
        """
        return self.session_metrics

    def refresh_from_database(self):
        """
        Fuerza la recarga del contexto desde la base de datos
        """
        self._loaded = False
        self._ensure_loaded()

        # También recargar métricas de sesión desde BD
        try:
            db_session = self.session_dao.get_session(self.session_id)
            if db_session:
                self.session_metrics = db_session
            else:
                # Si no existe en BD, mantener la actual y guardarla
                self.save_session_metrics()
        except Exception as e:
            logger.info(f"Error recargando métricas de sesión desde BD: {str(e)}")


class DistributedSessionManager:
    """
    Gestor de sesiones distribuidas que reemplaza al SessionSingleton
    """

    def create_context(self, session_id: str, headers: dict) -> DistributedContext:
        """
        Crea un contexto distribuido para la sesión dada

        Args:
            session_id: ID de la sesión

        Returns:
            DistributedContext: Contexto para la sesión
        """

        # Crear nuevo contexto distribuido
        context = DistributedContext(session_id, headers)

        # Configurar los managers con observers
        self._setup_managers_for_context(context)

        return context

    def _setup_managers_for_context(self, context: DistributedContext):
        """
        Configura los managers como observers del contexto distribuido
        """
        from app.managers.managers import (
            DataClienteManager,
            DataGestorManager,
            DataPreevalManager,
            DataOperacionManager,
            DataIntervinienteManager,
            RecomendacionHipotecaManager,
            DataMuestraInteresManager,
        )

        # Crear managers y añadir el contexto como observer
        cliente_manager = DataClienteManager()

        gestor_manager = DataGestorManager()

        preeval_manager = DataPreevalManager()

        operacion_manager = DataOperacionManager()

        interviniente_manager = DataIntervinienteManager()

        solicitud_hipoteca_manager = RecomendacionHipotecaManager()

        muestra_interes_manager = DataMuestraInteresManager()

        # Almacenar managers en el contexto para acceso posterior
        context.managers = {
            "clienteManager": cliente_manager,
            "gestorManager": gestor_manager,
            "preevalManager": preeval_manager,
            "operacionManager": operacion_manager,
            "intervinienteManager": interviniente_manager,
            "recomendacionHipotecaManager": solicitud_hipoteca_manager,
            "muestraInteresManager": muestra_interes_manager,
        }

        type_mapping = {
            "DataCliente": cliente_manager,
            "DataGestor": gestor_manager,
            "RecomendacionHipoteca": solicitud_hipoteca_manager,
            "DataPreeval": preeval_manager,
            "DataOperacion": operacion_manager,
            "DataInterviniente": interviniente_manager,
            "DataMuestraInteres": muestra_interes_manager,
        }

        for item in context.items.values():
            if item.item_type in type_mapping:
                # Reconstruir el manager
                item_manager = type_mapping[item.item_type]
                # Añadir cada item a su manager correspondiente
                item_manager.add_item(item)

        # Añadimos observers
        cliente_manager.add_observer(context)
        gestor_manager.add_observer(context)
        preeval_manager.add_observer(context)
        operacion_manager.add_observer(context)
        interviniente_manager.add_observer(context)
        solicitud_hipoteca_manager.add_observer(context)
        muestra_interes_manager.add_observer(context)

    def get_manager(self, session_id: str, manager_name: str):
        """
        Obtiene un manager específico para una sesión
        """
        if session_id in self._contexts:
            context = self._contexts[session_id]
            return getattr(context, "managers", {}).get(manager_name)
        return None

    def remove_session_context(self, session_id: str):
        """
        Elimina el contexto de una sesión de la memoria
        """
        if session_id in self._contexts:
            del self._contexts[session_id]


# Instancia global del gestor de sesiones distribuidas
distributed_session_manager = DistributedSessionManager()
