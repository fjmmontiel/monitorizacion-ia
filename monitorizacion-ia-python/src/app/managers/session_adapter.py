"""
Adaptador de sesión para migración de código legacy.

Este módulo proporciona adaptadores y protocolos para facilitar la migración
del sistema SessionSingleton obsoleto hacia el nuevo sistema DistributedContext.
Permite compatibilidad temporal mientras se actualiza el código existente.

Classes:
    - SessionProtocol: Protocolo común para interfaces de sesión
    - DistributedSessionAdapter: Adaptador para herramientas legacy

Purpose:
    - Proporcionar interfaz común entre sistemas antiguos y nuevos
    - Mantener compatibilidad temporal durante la transición
"""

from typing import Protocol, Any, Optional
from abc import ABC, abstractmethod


class SessionProtocol(Protocol):
    """
    Protocolo que define la interfaz común para sesiones
    """

    def get_context(self) -> Any:
        """Obtiene el contexto asociado a la sesión"""
        ...

    def get_manager(self, name: str) -> Optional[Any]:
        """Obtiene un manager específico por nombre"""
        ...


class DistributedSessionAdapter:
    """
    Adaptador para compatibilidad con herramientas que esperan SessionSingleton
    pero funcionan con DistributedContext
    """

    def __init__(self, distributed_context):
        self._distributed_context = distributed_context

    def get_context(self):
        """Retorna el contexto distribuido"""
        return self._distributed_context

    def get_manager(self, name: str):
        """Obtiene un manager del contexto distribuido"""
        return getattr(self._distributed_context, "managers", {}).get(name)
