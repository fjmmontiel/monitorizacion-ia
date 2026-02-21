"""
Herramientas de LangChain para gestión de datos de operaciones hipotecarias.

Incluye tools para crear, actualizar y eliminar datos de operaciones al panel de contexto durante el proceso de
contratación de productos hipotecarios.
"""

from typing import Type, Optional, List
from datetime import date, datetime
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field, PrivateAttr
import uuid

from app.constants.global_constants import GlobalConstants

from app.managers.session_adapter import SessionProtocol
from app.managers.items import EzDataOperacion
from app.managers.managers import DataOperacionManager, DataPreevalManager

from app.models.models import DatosOperacionSimple

from app.constants.global_constants import GlobalConstants

from app.services.tools_logger import LogToolMethod

#####################################################################################################
################################ TOOLS DATOS OPERACION ##############################################
#####################################################################################################


class EzOperacionBaseTool(BaseTool):
    """Clase base para herramientas de operación"""

    name: str = "operacion_base_tool"
    description: str = GlobalConstants.BASE_TOOL_DOCSTRING

    _session: SessionProtocol = PrivateAttr()

    def __init__(self, session: SessionProtocol):
        super().__init__()
        self._session = session

    def _get_operacion_by_name(self, nombre: str) -> EzDataOperacion:
        manager = self._session.get_manager("operacionManager")
        return manager.get_item(nombre)

    def _register_operacion(self, operacion: EzDataOperacion) -> None:
        self._session.get_manager("operacionManager").add_item(operacion)

    def _validacion_plazo_edad(
        self, datos: DatosOperacionSimple
    ) -> Optional[List[str]]:
        warning_plazo_maximo = []

        manager_cliente = self._session.get_manager("clienteManager")

        if len(manager_cliente.items) > 0:
            key = next(iter(manager_cliente.items))
            persona = manager_cliente.items[key]
            fecha_nacimiento_str = persona.data.get("fechaNacimiento")

        else:
            manager_interviniente = self._session.get_manager("intervinienteManager")
            if len(manager_interviniente.items) == 0:
                return None
            key = next(iter(manager_interviniente.items))
            persona = manager_interviniente.items[key]
            fecha_nacimiento_str = persona.data.get(
                "datos_personales_y_profesionales"
            ).get("fechaNacimiento")

        if not fecha_nacimiento_str:
            return None
        fecha_nacimiento = datetime.fromisoformat(fecha_nacimiento_str).date()
        hoy = date.today()
        edad = (
            hoy.year
            - fecha_nacimiento.year
            - ((hoy.month, hoy.day) < (fecha_nacimiento.month, fecha_nacimiento.day))
        )

        edad_al_final = edad + datos.plazoTotal

        if datos.finalidad == "2112":
            if datos.plazoTotal > 30 or edad_al_final > 75:
                warning_plazo_maximo.append(
                    f"El plazo ({datos.plazoTotal} años) y la edad del titular "
                    f"({edad} años) superan los límites permitidos para primera residencia "
                    f"(máx. 30 años y 75 años al vencimiento)."
                )

        elif datos.finalidad == "2113":
            if datos.plazoTotal > 30 or edad_al_final > 70:
                warning_plazo_maximo.append(
                    f"El plazo ({datos.plazoTotal} años) y la edad del titular "
                    f"({edad} años) superan los límites permitidos para segunda residencia "
                    f"(máx. 30 años y 70 años al vencimiento)."
                )

        return warning_plazo_maximo

    def _validacion_ltv(self, datos: DatosOperacionSimple) -> Optional[List[str]]:

        warning_loan_to_value = []

        manager_preeval: DataPreevalManager = self._session.get_manager(
            "preevalManager"
        )
        if len(manager_preeval.items) > 0:
            preeval = next(iter(manager_preeval.items))
            # Finalidad primera residencia
            if datos.finalidad == "2112":
                base = min(
                    manager_preeval.items[preeval].data["valorTasa"],
                    manager_preeval.items[preeval].data["precioVivienda"],
                )
                limite = 0.8 * base
            elif datos.finalidad == "2113":
                limite = min(
                    0.7 * manager_preeval.items[preeval].data["valorTasa"],
                    0.8 * manager_preeval.items[preeval].data["precioVivienda"],
                )

            if datos.importeSolicitado > limite:
                warning_loan_to_value.append(
                    f"""El importe solicitado {datos.importeSolicitado} supera 
                el límite permitdo {limite}:.
                Hasta el 80% del menor de los dos valores, tasación o precio de compra en escritura pública. 
                Para segunda residencia uso propio, el menor de los valores entre el 70% del valor de tasación 
                y el 80% del precio de compra en escritura."""
                )

        return warning_loan_to_value

    def _run(self, *args, **kwargs):
        """Implementación dummy para tests, no debe usarse en producción"""
        raise NotImplementedError(
            "EzOperacionBaseTool no debe ejecutarse directamente."
        )


# TOOL PARA CREAR Y AÑADIR UNA OPERACION
class CreateOperacionInput(BaseModel):
    """
    Esquema de entrada para crear y añadir una operación al panel de contexto.
    Contiene el nombre de la operación y los datos validados.
    """

    nombre: str = Field(
        description="""Nombre que recibirá el objeto de datos de la operación. Se debe utilizar un nombre
    amigable como 'Operación 1' e incrementar el número si se crean más"""
    )
    datos: DatosOperacionSimple = Field(
        description="Objeto con los datos validados de la operación que se deben almacenar."
    )


class CreateOperacionTool(EzOperacionBaseTool):
    """
    Herramienta para crear y añadir una operación en el panel de contexto.

    Uso:
    - Debe llamarse cada vez que se reciba cualquier dato del usuario, incluso si son parciales.
    - Si ya existe una operación con el mismo nombre, devuelve instrucciones para actualizar o confirmar con el usuario.
    - Si no se dispone de todos los datos necesarios para añadir la operación, deben registrarse como 'None' y el
    sistema debe notificar al usuario que los datos están incompletos.

    Argumentos:
        - nombre (str): Nombre único que identifica la operación.
        - datos (DatosOperacionSimple): Objeto que contiene los datos de la operación.

    Retorno:
    - Diccionario con:
        - mensaje: Estado del guardado y validación.
        - completo: Booleano indicando si la operación está completa.
    - En caso de error, devuelve un diccionario con la clave 'error' y el detalle.

    """

    name: str = "create_operacion"
    description: str = (
        "Almacena o actualiza los datos de una operación identificada por 'nombre'. "
    )
    args_schema: Type[BaseModel] = CreateOperacionInput
    return_direct: bool = False
    _session: SessionProtocol = PrivateAttr()

    def __init__(self, session: SessionProtocol):
        super().__init__(session)

    def _run(
        self, nombre: Optional[str] = None, datos: Optional[DatosOperacionSimple] = None
    ):
        try:
            LogToolMethod.log_initialization(self)

            if not nombre:
                return {"error": "No se ha proporcionado un nombre para la operación."}

            if not datos:
                return {
                    "error": f"No se han proporcionado datos para crear la operación '{nombre}'."
                }
            manager: DataOperacionManager = self._session.get_manager(
                "operacionManager"
            )
            if nombre in manager.items:
                return (
                    "Ya existe una operación con el mismo nombre en el panel de contexto. "
                    "Para actualizar sus datos llama a `update_operacion`."
                )

            # Genera un identificacdor un UUID único para el nombre del item.
            id = str(uuid.uuid4())

            datos_dict = datos.model_dump()
            item_operacion = EzDataOperacion(nombre, id, datos_dict)

            data_operacion = DatosOperacionSimple(**item_operacion.data)
            is_complete, validation_msg = data_operacion.validar()

            if not is_complete:
                return {
                    "mensaje": f"""No se ha podido crear la operación '{nombre}' en el panel de contexto porque se han
                     detectado errores en los datos: {validation_msg}""",
                    "completo": False,
                }
            else:
                # Validación para plazo máximo
                warning_plazo_maximo = self._validacion_plazo_edad(data_operacion)
                # Validación para LTV
                warning_loan_to_value = self._validacion_ltv(datos)
                manager.add_item(item_operacion)

                return {
                    "mensaje": f"""Los datos de la operación '{nombre}' han sido añadidos al panel de contexto.
                    Presenta de forma clara y estructura los datos que han sido añadidos al contexto
                    y haz visible tu razonamiento en el chat. 
                    Confirma con el usuario que todo es correcto antes de continuar.""",
                    "completo": True,
                    "warning_loan_to_value": warning_loan_to_value,
                    "warning_plazo_maximo": warning_plazo_maximo,
                }
        except Exception as e:
            mensaje = {
                "error": f"Error al añadir los datos de la operación al panel de contexto: {str(e)}"
            }
            LogToolMethod.log_failure(self, mensaje)
            return mensaje


# TOOL PARA ACTUALIZAR UNA OPERACION
class UpdateOperacionInput(BaseModel):
    """
    Esquema de entrada para actualizar una operación en el panel de contexto.
    Incluye el nombre de la operación y los datos validados a modificar.
    """

    nombre: Optional[str] = Field(
        description="Nombre de la operación que se desea actualizar."
    )
    datos: Optional[dict] = Field(
        description="Diccionario con los datos de la operación que se deben actualizar"
    )


class UpdateOperacionTool(EzOperacionBaseTool):
    """
    Herramienta que actualiza una operación existente en el panel de contexto.
    Argumentos:
       - nombre (str): Nombre único que identifica la operación.
        - datos (dict): Objeto que contiene los datos de la operación que se quiere actualizar.

    """

    name: str = "update_operacion"
    description: str = (
        """"Esa tool te permite actualizar los datos de una operación identificada por 'nombre'.
        Utiliza esta tool siempre que necesites actualizar datos de un objeto de tipo 'DatosOperacionSimple'."""
    )
    args_schema: Type[BaseModel] = UpdateOperacionInput
    return_direct: bool = False
    _session: SessionProtocol = PrivateAttr()

    def __init__(self, session: SessionProtocol):
        super().__init__(session)

    def _run(self, nombre: Optional[str] = None, datos: Optional[dict] = None):
        try:
            LogToolMethod.log_initialization(self)

            if not nombre:
                return {"error": "No se ha proporcionado el nombre de la operación."}

            if not datos:
                return {
                    "error": f"No se han proporcionado datos para actualizar la operación '{nombre}'."
                }

            # 1. RECUPERO MANANAGER
            manager: DataOperacionManager = self._session.get_manager(
                "operacionManager"
            )
            # 2. RECUPERO ITEM
            item_operacion = manager.get_item(nombre)
            # 3. ACTUALIZO ITEM
            item_operacion.update(datos)
            # 4. CONSTRUYO OBJETO Y VALIDO
            data_operacion = DatosOperacionSimple(**item_operacion.data)
            is_complete, validation_msg = data_operacion.validar()

            if is_complete:
                # Validación para plazo máximo
                warning_plazo_maximo = self._validacion_plazo_edad(data_operacion)
                # Validación para LTV
                warning_loan_to_value = self._validacion_ltv(data_operacion)

                manager.add_item(item_operacion)

                return {
                    "mensaje": f"""Datos de la operación '{nombre}' actualizados correctamente en el panel de contexto. 
                    Presenta de forma clara y estructurada los datos que han sido actualizados y haz visible tu 
                    razonamiento en el chat.  Confirma con el usuario que todo es correcto antes de continuar.""",
                    "completo": True,
                    "warning_loan_to_value": warning_loan_to_value,
                    "warning_plazo_maximo": warning_plazo_maximo,
                }

            else:
                return {
                    "mensaje": f"""Error de validación al actualizar los datos de la operación '{nombre}' en el panel
                    de contexto. Presenta de forma clara y estructurada los datos que son válidos y solicita los datos
                    necesarios para actualizar la operación correctamente.""",
                    "completo": False,
                    "errores": validation_msg,
                }

        except Exception as e:
            mensaje = {
                "error": f"Error al actualizar los datos de la operación en el panel de contexto: {str(e)}"
            }
            LogToolMethod.log_failure(self, mensaje)
            return mensaje


# TOOL PARA ELIMINAR UNA OPERACION
class DeleteOperacionInput(BaseModel):
    """
    Esquema de entrada para eliminar una operación del panel de contexto.
    """

    nombre: str = Field(description="Nombre de la operación que se desea eliminar.")


class DeleteOperacionTool(EzOperacionBaseTool):
    """
    Herramienta que elimina una operación del panel de contexto a partir de su nombre.
    """

    name: str = "delete_operacion"
    description: str = "Elimina una operación del panel de contexto dado su nombre"
    args_schema: Type[BaseModel] = DeleteOperacionInput
    return_direct: bool = False
    _session: SessionProtocol = PrivateAttr()

    def __init__(self, session: SessionProtocol):
        super().__init__(session)

    def _run(self, nombre: str):

        try:
            LogToolMethod.log_initialization(self)
            
            manager: DataOperacionManager = self._session.get_manager(
                "operacionManager"
            )
            operacion = self._get_operacion_by_name(nombre)
            manager.remove_item(operacion)
            return (
                f"Operación '{nombre}' eliminada correctamente del panel de contexto."
            )
        except Exception as e:
            mensaje = f"Error eliminando la operación '{nombre}' del panel de contexto: {str(e)}"
            LogToolMethod.log_failure(self, mensaje)
            return mensaje
