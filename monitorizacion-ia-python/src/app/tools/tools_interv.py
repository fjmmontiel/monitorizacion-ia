"""
Herramientas de LangChain para gesión de datos de intervinientes.

Incluye tools para crear, actualizar y eliminar información de intervinientes que participan en operaciones de
contratación de productos hipotecarios.
"""

from typing import Type, Optional, List
import uuid
from datetime import date, datetime

from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field, PrivateAttr

from app.constants.global_constants import GlobalConstants

from app.managers.session_adapter import SessionProtocol
from app.managers.items import EzDataInterviniente
from app.managers.managers import DataIntervinienteManager, DataClienteManager

from app.models.models import DatosIntervSimple

from app.services.tools_logger import LogToolMethod

#####################################################################################################
################################ TOOLS INTERVINIENTES ###############################################
#####################################################################################################
class EzIntervinienteBaseTool(BaseTool):
    """Clase base para herramientas de intervinientes"""

    name: str = "interviniente_base_tool"
    description: str = GlobalConstants.BASE_TOOL_DOCSTRING

    _session: SessionProtocol = PrivateAttr()

    def __init__(self, session: SessionProtocol):
        super().__init__()
        self._session = session

    def _get_interviniente_by_name(self, nombre: str) -> EzDataInterviniente:
        manager = self._session.get_manager("intervinienteManager")
        return manager.get_item(nombre)

    def _register_interviniente(self, interviniente: EzDataInterviniente) -> None:
        self._session.get_manager("intervinienteManager").add_item(interviniente)

    def _validacion_plazo_edad(self, datos: DatosIntervSimple) -> Optional[List[str]]:

        warning_plazo_maximo = []
        fecha_nacimiento_str = None

        manager_operacion = self._session.get_manager("operacionManager")

        # Existe una operación
        if len(manager_operacion.items) > 0:
            fecha_nacimiento_str = (
                datos.datos_personales_y_profesionales.fechaNacimiento
            )
        if not fecha_nacimiento_str:
            return None

        fecha_nacimiento = datetime.fromisoformat(fecha_nacimiento_str).date()
        hoy = date.today()
        edad = (
            hoy.year
            - fecha_nacimiento.year
            - ((hoy.month, hoy.day) < (fecha_nacimiento.month, fecha_nacimiento.day))
        )

        # Info de la operación
        key = next(iter(manager_operacion.items))
        operacion = manager_operacion.items[key]
        data_operacion = operacion.data

        # Info del interviniente
        edad_al_final = edad + data_operacion.get("plazoTotal")

        if data_operacion.get("finalidad") == "2112":
            if data_operacion.get("plazoTotal") > 30 or edad_al_final > 75:
                warning_plazo_maximo.append(
                    f"El plazo ({data_operacion.get('plazoTotal')} años) y la edad del titular "
                    f"({edad} años) superan los límites permitidos para primera residencia "
                    f"(máx. 30 años y 75 años al vencimiento)."
                )

        elif data_operacion.get("finalidad") == "2113":
            if data_operacion.get("plazoTotal") or edad_al_final > 70:
                warning_plazo_maximo.append(
                    f"El plazo ({data_operacion.get('plazoTotal')} años) y la edad del titular "
                    f"({edad} años) superan los límites permitidos para segunda residencia "
                    f"(máx. 30 años y 70 años al vencimiento)."
                )

        return warning_plazo_maximo

    def _run(self, *args, **kwargs):
        """Implementación dummy para tests, no debe usarse en producción"""
        raise NotImplementedError(
            "EzIntervinienteBaseTool no debe ejecutarse directamente."
        )


# TOOL PARA CREAR UN INTERVINIENTE
class CreateIntervInput(BaseModel):
    """
    Esquema de entrada para crear un interviniente en el panel de contexto.
    """

    nombre: str = Field(
        description="""Nombre que recibirá el objeto de datos del interviniente. Se debe utilizar un nombre amigable
                        como 'Interviniente 1' e incrementar el número si se crean más."""
    )
    datos: DatosIntervSimple = Field(
        description="Objeto con los datos validados del interviniente que se deben almacenar."
    )


class CreateIntervTool(EzIntervinienteBaseTool):
    """
    Herramienta que crea y persiste los datos de un interviniente en el panel de contexto.
    """

    name: str = "create_interviniente"
    description: str = (
        "Almacena los datos de un interviniente identificado por 'nombre' en el panel de contexto."
    )
    args_schema: Type[BaseModel] = CreateIntervInput
    return_direct: bool = False
    _session: SessionProtocol = PrivateAttr()

    def __init__(self, session: SessionProtocol):
        super().__init__(session)

    def _run(
        self, nombre: Optional[str] = None, datos: Optional[DatosIntervSimple] = None
    ):
        try:
            LogToolMethod.log_initialization(self)
            if not nombre:
                return {
                    "error": "No se ha proporcionado un nombre para el interviniente."
                }

            if not datos:
                return {
                    "error": f"No se han proporcionado datos para crear el interviniente '{nombre}'."
                }

            manager: DataIntervinienteManager = self._session.get_manager(
                "intervinienteManager"
            )
            if nombre in manager.items:
                return (
                    "Ya existe un interviniente con el mismo nombre en el panel de contexto. "
                    "Para actualizar sus datos llama a `update_interviniente`."
                )

            if len(manager.items) >= 2:
                return "Ya existen dos intervinientes para esta muestra de interés. El máximo es dos."

            manager_cliente: DataClienteManager = self._session.get_manager(
                "clienteManager"
            )
            # Si no hay intervinientes y hay un cliente en el panel de contexto
            if len(manager.items) == 0 and len(manager_cliente.items) == 1:
                cliente = next(iter(manager_cliente.items))
                if (
                    manager_cliente.items[cliente].data["nif"]
                    != datos.datos_personales_y_profesionales.nif
                ):
                    return """Primero se debe registrar el primer interviniente y debe coincidir con 
                    el cliente guardado.
                    El cliente guardado en el panel de contexto no se puede modificar."""

            # Genera un identificacdor un UUID único para el nombre del item.
            id = str(uuid.uuid4())

            # 1) EzDataInterviniente en memoria
            datos_dict = datos.model_dump()
            item_interviniente = EzDataInterviniente(nombre, id, datos_dict)

            data_interviniente = DatosIntervSimple(**item_interviniente.data)
            errores = data_interviniente.validar()

            is_complete = len(errores) == 0
            validation_msg = "\n".join(errores)

            if is_complete:
                # Validación para plazo máximo
                warning_plazo_maximo = self._validacion_plazo_edad(data_interviniente)
                manager.add_item(item_interviniente)
                return {
                    "mensaje": f"""Los datos del interviniente '{nombre}' han sido añadidos correctamente
                    al panel de contexto. Haz visible tu razonamiento en el chat y presenta
                    de forma clara y estructurada los datos del interviniente que han sido informados.
                    Confirma con el usuario que todo es correcto antes de continuar.""",
                    "completo": True,
                    "warning_plazo_maximo": warning_plazo_maximo,
                }
            else:
                return {
                    "mensaje": f"""No se ha podido crear el interviniente '{nombre}' porque los datos están 
                    incompletos. Haz visible tu razonamiento en el chat y presenta de forma clara y 
                    estructurada los datos del interviniente que han sido informados y los que no lo están.""",
                    "completo": False,
                    "errores": validation_msg,
                }

        except Exception as e:
            mensaje = f"Error: Ha ocurrido un error al añadir los datos del interviniente al panel de contexto: {e}"
            LogToolMethod.log_failure(self, mensaje)
            return mensaje


# TOOL PARA ACTUALIZAR UN INTERVINIENTE
class UpdateIntervInput(BaseModel):
    """
    Esquema de entrada para actualizar un interviniente en el panel de contexto.
    """

    nombre: Optional[str] = Field(
        default=None, description="Nombre único del objeto del interviniente."
    )
    datos: Optional[dict] = Field(
        default=None,
        description="Objeto con los datos del interviniente que se deben actualizar.",
    )


class UpdateIntervTool(EzIntervinienteBaseTool):
    """
    Actualiza los datos de un interviniente identificado por 'nombre' en el panel de contexto.

    **Uso obligatorio antes de llamar a la herramienta `guardar_muestra_de_interes`:**
    - Siempre que se reciban nuevos datos del interviniente, debes actualizar el contexto utilizando esta herramienta.

    **Parámetros obligatorios:**
        - `nombre` (str): Nombre único del interviniente que se está actualizando (ejemplo: "Interviniente titular").
        - `datos` (dict): Objeto con todos los datos del interviniente que se quieren actualizar

    **Returns:**
        dict: Resultado de la actualización, o un diccionario con el campo "error" si algo falla.
    """

    name: str = "update_interviniente"
    description: str = (
        """Actualiza los datos de un interviniente identificado por 'nombre' en el panel de contexto. 
        Debe usarse siempre que se reciban nuevos datos del interviniente antes de llamar a la 
        herramienta `guardar_muestra_de_interes`."""
    )
    args_schema: Type[BaseModel] = UpdateIntervInput
    return_direct: bool = False
    _session: SessionProtocol = PrivateAttr()

    def __init__(self, session: SessionProtocol):
        super().__init__(session)

    def _run(self, nombre: Optional[str] = None, datos: Optional[dict] = None):
        try:
            LogToolMethod.log_initialization(self)
            if not nombre:
                return {"error": "No se ha proporcionado el nombre del interviniente."}

            if not datos:
                return {
                    "error": f"No se han proporcionado datos para actualizar el interviniente '{nombre}'."
                }

            # 1. RECUPERO MANAGER
            manager: DataIntervinienteManager = self._session.get_manager(
                "intervinienteManager"
            )
            # 2. RECUPERO ITEM
            item_interviniente = manager.get_item(nombre)
            # 3. ACTUALIZO ITEM
            item_interviniente.update(datos)
            # 4. CONSTRUYO OBJETO Y VALIDO
            data_interviniente = DatosIntervSimple(**item_interviniente.data)
            errores = data_interviniente.validar()
            is_complete = len(errores) == 0
            validation_msg = "\n".join(errores)

            if is_complete:
                # Validación para plazo máximo
                warning_plazo_maximo = self._validacion_plazo_edad(data_interviniente)
                manager.add_item(item_interviniente)

                return {
                    "mensaje": f"""Los datos del interviniente '{nombre}' han sido actualizados correctamente
                    en el panel de contexto. Haz visible tu razonamiento en el chat y presenta de forma clara y 
                    estructurada los datos que han sido actualizados. 
                    Por favor, si lo hay, continua con el segundo interviniente. 
                    """,
                    "completo": True,
                    "warning_plazo_maximo": warning_plazo_maximo,
                }
            else:
                return {
                    "mensaje": f"""Los datos del interviniente '{nombre}' no han podido actualizarse en el panel de
                    contexto porque están incompletos. Para actualizar el interviniente con nombre '{nombre}' solicita
                    el resto de campos necesarios.
                    """,
                    "completo": False,
                    "errores": validation_msg,
                }

        except Exception as e:
            mensaje = {
                "error": f"Error al actualizar los datos del interviniente en el panel de contexto: {str(e)}"
            }
            LogToolMethod.log_failure(self, mensaje)
            return mensaje


# TOOL PARA ELIMINAR UN INTERVINIENTE
class DeleteIntervInput(BaseModel):
    """
    Esquema de entrada para eliminar un interviniente del panel de contexto según su nombre.
    """

    nombre: str = Field(
        description="Nombre único del objeto del interviniente que se desea borrar panel de contexto."
    )


class DeleteIntervTool(EzIntervinienteBaseTool):
    """Herramienta para eliminar un interviniente del panel de contexto."""

    name: str = "delete_interviniente"
    description: str = "Elimina un interviniente del panel de contexto dado su nombre"
    args_schema: Type[BaseModel] = DeleteIntervInput
    return_direct: bool = False
    _session: SessionProtocol = PrivateAttr()

    def __init__(self, session: SessionProtocol):
        super().__init__(session)

    def _run(self, nombre: str):
        try:
            LogToolMethod.log_initialization(self)
            manager: DataIntervinienteManager = self._session.get_manager(
                "intervinienteManager"
            )
            interv = self._get_interviniente_by_name(nombre)
            manager.remove_item(interv)
            return f"Interviniente '{nombre}' eliminado correctamente del panel de contexto."

        except Exception as e:
            mensaje = f"Error eliminando el interviniente '{nombre}' del panel de contexto: {str(e)}"
            LogToolMethod.log_failure(self, mensaje)
            return mensaje
