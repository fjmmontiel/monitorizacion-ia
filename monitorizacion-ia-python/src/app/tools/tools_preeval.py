"""
Herramientas de LangChain para gestión de datos de una preevaluación hipotecaria.

Incluye tools para crear, actualizar y eliminar datos de preevaluación durante el proceso de análisis previo
de productos hipotecarios.
"""

from typing import Type, Optional

from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field, PrivateAttr
import uuid

from app.constants.global_constants import GlobalConstants

from app.managers.session_adapter import SessionProtocol
from app.managers.items import EzDataPreeval
from app.managers.managers import DataPreevalManager

from app.models.models import DatosPreEvalSimple


from app.constants.global_constants import GlobalConstants

from app.services.tools_logger import LogToolMethod

#####################################################################################################
################################ TOOLS DATOS PREEVALUACION ##########################################
#####################################################################################################


class EzPreevalBaseTool(BaseTool):
    """Clase base para herramientas de preevaluación"""

    name: str = "preeval_base_tool"
    description: str = GlobalConstants.BASE_TOOL_DOCSTRING

    _session: SessionProtocol = PrivateAttr()

    def __init__(self, session: SessionProtocol):
        super().__init__()
        self._session = session

    def _get_preeval_by_name(self, nombre: str) -> EzDataPreeval:
        manager = self._session.get_manager("preevalManager")
        return manager.get_item(nombre)

    def _register_preeval(self, preeval: EzDataPreeval) -> None:
        self._session.get_manager("preevalManager").add_item(preeval)

    def _run(self, *args, **kwargs):
        """Implementación dummy para tests, no debe usarse en producción"""
        raise NotImplementedError("EzPreevalBaseTool no debe ejecutarse directamente.")


# TOOL PARA CREAR UNA PREEVALUACIÓN
class CreatePreevalInput(BaseModel):
    """
    Esquema de entrada para crear una preevaluación en el panel de contexto.
    Contiene el nombre y los datos validados.
    """

    nombre: str = Field(
        description="""Nombre que recibirá el objeto de datos de la preevaluación. Se debe utilizar un nombre 
                        amigable como 'Preevaluación 1' e incrementar el número si se crean más"""
    )
    datos: DatosPreEvalSimple = Field(
        description="Objeto con los datos validados de preevaluación que se deben almacenar."
    )


class CreatePreevalTool(EzPreevalBaseTool):
    """
    Herramienta que crea una preevaluación en el panel de contexto.

    IMPORTANTE:
    - El campo 'importeTotalInversion' no debe ser inferido automáticamente como igual al 'precioVivienda' si no
    se proporciona explícitamente.
    - Si el usuario no proporciona el valor de 'importeTotalInversion', el sistema debe seguir el flujo definido
    en el prompt del sistema para calcular los gastos hipotecarios antes de añadir la preevaluación al
    panel de contexto.
    - Si no se dispone de todos los datos necesarios para calcular los gastos hipotecarios, este campo debe
    registrarse como 'None' y el sistema debe notificar al usuario que los datos están incompletos.

    NOTA:
    - Si ya existe una preevaluación con el mismo nombre, el sistema debe informar al usuario y sugerirle que
    utilice la herramienta 'update_preeval' para actualizar los datos existentes o que modifique el nombre para
    crear una nueva preevaluación.
    """

    name: str = "create_preeval"
    description: str = (
        "Almacena los datos de una preevaluación identificada por 'nombre' en el panel de contexo."
    )
    args_schema: Type[BaseModel] = CreatePreevalInput
    return_direct: bool = False
    _session: SessionProtocol = PrivateAttr()

    def __init__(self, session: SessionProtocol):
        super().__init__(session)

    def _run(
        self, nombre: Optional[str] = None, datos: Optional[DatosPreEvalSimple] = None
    ):
        try:
            LogToolMethod.log_initialization(self)

            if not nombre:
                return {
                    "error": "No se ha proporcionado un nombre para la preevaluación."
                }

            if not datos:
                return {
                    "error": f"No se han proporcionado datos para crear la preevaluación '{nombre}'."
                }

            manager: DataPreevalManager = self._session.get_manager("preevalManager")

            if nombre in manager.items:
                return (
                    "Ya existe una preevaluación con el mismo nombre en el panel de contexto. "
                    "Para actualizar sus datos llama a `update_preeval`."
                )

            # Genera un identificacdor un UUID único para el nombre del item.
            id = str(uuid.uuid4())

            # 1) convertir datos Pydantic -> dict y crear EzDataPreeval en memoria
            datos_dict = datos.model_dump()
            item_preeval = EzDataPreeval(nombre, id, datos_dict)

            data_preeval = DatosPreEvalSimple(**item_preeval.data)
            errores = data_preeval.validar()
            is_complete = len(errores) == 0
            validation_msg = "\n".join(errores)

            if is_complete:
                manager.add_item(item_preeval)
                return {
                    "mensaje": f"""La preevaluación '{nombre}' ha sido añadida correctamente al panel de contexto.
                    Presenta de forma clara y estructura los datos que han sido añadidos al contexto
                    y haz visible tu razonamiento en el chat. 
                    Confirma con el usuario que todo es correcto antes de continuar.""",
                    "completo": True,
                }
            else:
                return {
                    "mensaje": f"""No se puede añadir la preevaluación '{nombre}' al contexto porque se han detectado
                    errores en los datos.""",
                    "completo": False,
                    "errores": validation_msg,
                }

        except Exception as e:
            mensaje = {
                "error": f"Error al añadir al panel de contexto los datos de preevaluación: {str(e)}"
            }
            LogToolMethod.log_failure(self, mensaje)
            return mensaje


# TOOL PARA ACTUALIZAR UNA PREEVALUACIÓN
class UpdatePreevalInput(BaseModel):
    """
    Esquema de entrada para actualizar una preevaluación en el panel de contexto.
    Incluye el nombre de la preevaluación y los datos validados a modificar.
    """

    nombre: Optional[str] = Field(
        description="Nombre de la preevaluación que se desea actualizar en el panel de contexto."
    )
    datos: Optional[dict] = Field(
        default=None,
        description="Diccionario con los datos de la preevaluación que se deben actualizar",
    )


class UpdatePreevalTool(EzPreevalBaseTool):
    """
    Herramienta que actualiza una preevaluación existente en el panel de contexto.
    """

    name: str = "update_preeval"
    description: str = "Actualiza los datos de una preevaluación."
    args_schema: Type[BaseModel] = UpdatePreevalInput
    return_direct: bool = False
    _session: SessionProtocol = PrivateAttr()

    def __init__(self, session: SessionProtocol):
        super().__init__(session)

    def _run(self, nombre: Optional[str] = None, datos: Optional[dict] = None):
        try:
            LogToolMethod.log_initialization(self)

            if not nombre:
                return {
                    "error": "No se ha proporcionado el nombre de la preevaluación."
                }

            if not datos:
                return {
                    "error": f"No se han proporcionado datos para actualizar la preevaluación '{nombre}'."
                }

            # 1. RECUPERO MANAGER
            manager: DataPreevalManager = self._session.get_manager("preevalManager")
            # 2. RECUPERO ITEM
            item_preeval = manager.get_item(nombre)
            # 3. ACTUALIZO ITEM
            item_preeval.update(datos)
            # 4. CONSTRUYO OBJETO Y VALIDO
            data_preeval = DatosPreEvalSimple(**item_preeval.data)
            errores = data_preeval.validar()
            is_complete = len(errores) == 0
            validation_msg = "\n".join(errores)

            if is_complete:
                manager.add_item(item_preeval)
                return f"""Datos de la preevaluación '{nombre}' actualizados correctamente en el panel de contexto.
                Presenta de forma clara y estructurada los datos que han sido actualizados y haz
                 visible tu razonamiento en el chat. Confirma con el usuario que todo es correcto antes de continuar.
                """
            else:
                return {
                    "mensaje": f"""Error de validación al actualizar los datos de la preevaluación '{nombre}':
                    Presenta de forma clara y estructurada los datos que son válidos. Informa al usuario sobre el 
                    error y solicita los datos necesarios para actualizar correctamente.""",
                    "completo": False,
                    "errores": validation_msg,
                }

        except Exception as e:
            mensaje = {
                "error": f"Error al actualizar los datos de la preevaluación panel de contexto: {str(e)}"
            }
            LogToolMethod.log_failure(self, mensaje)
            return mensaje


# TOOL PARA ELIMINAR UNA PREEVALUACIÓN
class DeletePreevalInput(BaseModel):
    """
    Esquema de entrada para eliminar una preevaluación del panel de contexto.
    Requiere el nombre de la preevaluación que se desea eliminar.
    """

    nombre: str = Field(description="Nombre de la preevaluación que se desea eliminar")


class DeletePreevalTool(EzPreevalBaseTool):
    """
    Herramienta que elimina una preevaluación del panel de contexto a partir de su nombre.
    """

    name: str = "delete_preeval"
    description: str = "Elimina una preevaluación del panel de contexto dado su nombre"
    args_schema: Type[BaseModel] = DeletePreevalInput
    return_direct: bool = False
    _session: SessionProtocol = PrivateAttr()

    def __init__(self, session: SessionProtocol):
        super().__init__(session)

    def _run(self, nombre: str):
        try:
            LogToolMethod.log_initialization(self)

            manager: DataPreevalManager = self._session.get_manager("preevalManager")
            preeval = self._get_preeval_by_name(nombre)
            manager.remove_item(preeval)
            return (
                f"Preevaluación '{nombre}' eliminada correctamente panel de contexto."
            )
        except Exception as e:
            mensaje = f"Error eliminando la preevaluación '{nombre}' del panel de contexto: {str(e)}"
            LogToolMethod.log_failure(self, mensaje)
            return mensaje
