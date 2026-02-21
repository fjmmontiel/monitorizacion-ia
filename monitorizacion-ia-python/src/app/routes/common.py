"""Funciones comunes para las rutas de la aplicación"""

from app.services.llm_service import LangchainLLMService


def get_llm_service() -> LangchainLLMService:
    """Retorna una instancia del servicio LLM de Lnagchain"""

    return LangchainLLMService()
