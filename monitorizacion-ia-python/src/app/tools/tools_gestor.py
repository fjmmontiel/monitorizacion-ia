"""
Herramientas de LangChain para gestión de datos del gestor.

Incluye tools para crear y validar información del gestor que maneja el proceso.
"""

from typing import Type

from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field, PrivateAttr
import uuid

from app.managers.session_adapter import SessionProtocol
from app.managers.items import EzDataGestor
from app.managers.managers import DataGestorManager
from app.models.models_resto import DatosGestor


from app.constants.global_constants import GlobalConstants

from app.services.tools_logger import LogToolMethod

#####################################################################################################
#################################### TOOLS GESTOR ###################################################
#####################################################################################################
class EzDatosGestor(BaseTool):
    """Clase base para herramientas del gestor"""

    name: str = "gestor_base_tool"
    description: str = GlobalConstants.BASE_TOOL_DOCSTRING
    _session: SessionProtocol = PrivateAttr()

    def __init__(self, session: SessionProtocol):
        super().__init__()
        self._session = session

    def _get_gestor_by_name(self, nombre: str) -> EzDataGestor:
        manager = self._session.get_manager("gestorManager")
        return manager.get_item(nombre)

    def _run(self, *args, **kwargs):
        """Implementación dummy para tests, no debe usarse en producción"""
        raise NotImplementedError(
            "EzDatosGestorBaseTool no debe ejecutarse directamente."
        )


# TOOL PARA CREAR DATOS DEL GESTOR
class CreateGestorInput(BaseModel):
    """
    Esquema de entrada para crear un gestor en el panel de contexto.
    Contiene los datos validados y el nombre.
    """

    nombre: str = Field(description="Nombre único del objeto del gestor.")
    datos: DatosGestor = Field(
        description="Objeto con los datos del gestor que se deben almacenar."
    )


class CreateGestorTool(EzDatosGestor):
    """
    Herramienta que crea y persiste los datos de un gestor en el panel de contexto.
    """

    name: str = "create_gestor"
    description: str = (
        "Almacena o actualiza los datos de un gestor identificado por 'código' en el panel de contexto."
    )
    args_schema: Type[BaseModel] = CreateGestorInput
    return_direct: bool = False
    _session: SessionProtocol = PrivateAttr()

    def __init__(self, session: SessionProtocol):
        super().__init__(session)

    def _run(self, nombre: str, datos: DatosGestor):
        try:
            LogToolMethod.log_initialization(self)

            # Genera un identificacdor un UUID único para el nombre del item.
            id = str(uuid.uuid4())

            # 1) convertir datos Pydantic -> dict y crear EzDataGestor en memoria
            datos_dict = datos.model_dump()
            is_complete = True
            edg = EzDataGestor(name=nombre, id=id, data=datos_dict)

            # 2) validar usando validate_data del manager
            manager: DataGestorManager = self._session.get_manager("gestorManager")
            is_complete = True
            validation_msg = ""
            try:
                res = manager.validate_data(nombre)
                if isinstance(res, tuple):
                    is_complete, validation_msg = res
                elif isinstance(res, bool):
                    is_complete = res
            except Exception:
                is_complete = False
                validation_msg = "Error: Ha ocurrido un error al añadir los datos del gestor al panel de contexto."

            # 3) devolver resultado coherente
            if is_complete:
                manager.add_item(edg)
                return {
                    "mensaje": f"""Los datos del gestor '{nombre}' han sido añadidos correctamente al panel 
                    de contexto.""",
                    "completo": True,
                }
            else:
                return {
                    "mensaje": "Ya existe un gestor cargado en el panel de contexto y solamente puede haber uno.",
                    "completo": False,
                    "errores": validation_msg,
                }

        except Exception as e:
            mensaje = f"Error: Ha ocurrido un error al añadir los datos del gestor al panel de contexto: {e}"
            LogToolMethod.log_failure(self, mensaje)
            return mensaje
