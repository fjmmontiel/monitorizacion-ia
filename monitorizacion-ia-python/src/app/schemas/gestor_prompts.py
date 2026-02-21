"""
Este módulo define los esquemas de datos para el gestor de prompts.
"""

from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class GetPromptRequest(BaseModel):
    """ Modulo """
    feature:str
    model_id:Optional[str]=None
    version:Optional[str]=None

class PromptResponse(BaseModel):
    """ Modulo """
    prompt_id:str
    application_id:str
    model_id:str
    feature:str
    content:str
    tags:str
    created_by:str
    created_at:datetime
    version:Optional[str]=None
    usage_count:int