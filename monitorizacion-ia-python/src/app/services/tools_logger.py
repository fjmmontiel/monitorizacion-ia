"""
Modulo para loggeo de tools

Clases:
    LogToolFunction: loggeo de tools en formato función con decorador @tool
    LogToolMethod: loggeo para tools que son clases que heredan de BaseTool
"""

import inspect
from functools import wraps

from langchain_core.tools import BaseTool

from app.services import llm_service

from app.managers.distributed_context import DistributedContext

from qgdiag_lib_arquitectura import CustomLogger

logger = CustomLogger("tools")

class LogToolFunction(object):
    """
    Clase para loggear tools con formato de funcion (llevan decorador @tool())
    """    

    @staticmethod
    def log_initialization(tool_name: str, current_context: DistributedContext = None):
        """Loggea la inicialización de la ejecución de una tool

        Args:
            tool_name (str): nombre de la tool
            current_context (DistributedContext, optional): Contexto de la Tool. Defaults to None.
        """        
        session_id = ''
        gestor = ''
        if current_context:
            session_id = current_context.session_id
            gestor = current_context.get_session_metrics().gestor

        logger.info(f"Session_id={session_id}. Gestor={gestor} # Ejecutando Tool {tool_name}")

    @staticmethod
    def log_failure(tool_name: str, exception, current_context: DistributedContext = None):
        """Loggea el resultado de la ejecución de una tool que es erróneo

        Args:
            tool_name (str): nombre de la tool
            current_context (DistributedContext, optional): Contexto de la Tool. Defaults to None.
        """
        session_id = ''
        gestor = ''
        if current_context:
            session_id = current_context.session_id
            gestor = current_context.get_session_metrics().gestor
        logger.info(f"Session_id={session_id}. Gestor={gestor} # Tool {tool_name} - Error {exception}")

class LogToolMethod(object):
    """
    Clase para loggear tools que son clases que heredan de BaseTool
    """  

    @staticmethod
    def log_initialization(tool_object: BaseTool):
        """Loggea la inicialización de la ejecución de una tool

        Args:
            tool_object (BaseTool): objeto Tool que es ejecutado
        """        
        session_id = ''
        gestor = ''
        tool_name = ''
        if tool_object and tool_object._session and tool_object._session.get_context():
            session_id = tool_object._session.get_context().session_id
            gestor = tool_object._session.get_context().get_session_metrics().gestor
            tool_name = tool_object.name

        logger.info(f"Session_id={session_id}. Gestor={gestor} # Ejecutando Tool {tool_name}")

    @staticmethod
    def log_failure(tool_object: BaseTool, mensaje_error):
        """Loggea el resultado de la ejecución de una tool que es erróneo

        Args:
            tool_object (BaseTool): objeto Tool que es ejecutado
        """
        session_id = ''
        gestor = ''
        tool_name = ''
        if tool_object and tool_object._session and tool_object._session.get_context():
            session_id = tool_object._session.get_context().session_id
            gestor = tool_object._session.get_context().get_session_metrics().gestor
            tool_name = tool_object.name

        logger.info(f"Session_id={session_id}. Gestor={gestor} # Tool {tool_name} - Error {str(mensaje_error)}")