"""
Herramientas de LangChain para gestión de datos del cliente.

Incluye tools para crear el objeto del cliente que está partipando en el proceso.
"""

from typing import Type

from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field, PrivateAttr
import uuid

from app.managers.session_adapter import SessionProtocol
from app.models.models_resto import DatosCliente
from app.managers.items import EzDataCliente
from app.managers.managers import DataClienteManager

from app.constants.global_constants import GlobalConstants

from app.services.tools_logger import LogToolMethod
#####################################################################################################
#################################### TOOLS CLIENTE ##################################################
#####################################################################################################
class EzDatosCliente(BaseTool):
    """Clase base para herramientas del cliente"""

    name: str = "cliente_base_tool"
    description: str = GlobalConstants.BASE_TOOL_DOCSTRING
    _session: SessionProtocol = PrivateAttr()

    def __init__(self, session: SessionProtocol):
        super().__init__()
        self._session = session

    def _get_cliente_by_name(self, nombre: str) -> EzDataCliente:
        manager = self._session.get_manager("clienteManager")
        return manager.get_item(nombre)

    def _run(self, *args, **kwargs):
        """Implementación dummy para tests, no debe usarse en producción"""
        raise NotImplementedError(
            "EzDatosClienteBaseTool no debe ejecutarse directamente."
        )


# TOOL PARA CREAR DATOS DEL CLIENTE
class CreateClienteInput(BaseModel):
    """
    Esquema de entrada para crear un cliente y añadirlo al panel de contexto.
    Contiene los datos validados y el nombre.
    """

    nombre: str = Field(
        description="""Nombre único del objeto del cliente. Si es cliente se debe poner 'Cliente' y
            si es precliente se debe poner 'Precliente'."""
    )
    datos: DatosCliente = Field(
        description="Objeto con los datos del cliente que se deben almacenar."
    )


class CreateClienteTool(EzDatosCliente):
    """Tool para crear los datos de un cliente"""

    name: str = "create_cliente"
    description: str = (
        "Añade los datos de un cliente identificado por 'nif' al panel de contexto"
        "Debe usarse inmediatamente después de la tool 'consultar_cliente_por_nif'. "
    )
    args_schema: Type[BaseModel] = CreateClienteInput
    return_direct: bool = False
    _session: SessionProtocol = PrivateAttr()

    def __init__(self, session: SessionProtocol):
        super().__init__(session)

    def _run(self, nombre: str, datos: DatosCliente):
        try:
            LogToolMethod.log_initialization(self)
            # Genera un identificacdor un UUID único para el nombre del item.
            id = str(uuid.uuid4())

            # 1) convertir datos Pydantic -> dict y crear EzDataCliente en memoria
            datos_dict = datos.model_dump()
            is_complete = True
            edc = EzDataCliente(name=nombre, id=id, data=datos_dict)

            # 2) validar usando validate_data del manager
            manager: DataClienteManager = self._session.get_manager("clienteManager")
            if len(manager.items) != 0:
                return """Ya existe un cliente en el panel de contexto. Es necesario iniciar una nueva sesión para
                    operar con un cliente distinto.
                    Deriva al gestor a la visión 360º en caso de que quiera cambiar de cliente.
                    """

            is_complete = True
            validation_msg = ""
            try:
                manager.add_item(edc)
                res = manager.validate_data(nombre)
                if isinstance(res, tuple):
                    is_complete, validation_msg = res
                elif isinstance(res, bool):
                    is_complete = res
            except Exception:
                is_complete = False
                validation_msg = "Error: Ha ocurrido un error al añadir los datos del cliente al panel de contexto."

            # 3) devolver resultado coherente
            if is_complete:
                return {
                    "mensaje": f"Los datos del cliente '{nombre}' han sido añadidos al panel de contexto.",
                    "completo": True,
                }
            else:
                return {
                    "mensaje": f"""Los datos del cliente '{nombre}' han sido añadidos al panel de contexto,
                    pero están incompletos.""",
                    "completo": False,
                    "errores": validation_msg,
                }

        except Exception as e:
            mensaje = f"Error: Ha ocurrido un error al añadir los datos del cliente al panel de contexto: {e}"
            LogToolMethod.log_failure(self, mensaje)
            return mensaje


# TOOL PARA ELIMINAR UN CLIENTE
class DeleteClienteInput(BaseModel):
    """
    Esquema de entrada para eliminar un cliente del panel de contexto según su nombre.
    """

    nombre: str = Field(
        description="Nombre único del objeto del cliente que se desea borrar."
    )


class DeleteClienteTool(EzDatosCliente):
    """Herramienta para eliminar un cliente del panel de contexto."""

    name: str = "delete_cliente"
    description: str = "Elimina un cliente del panel contexto dado su nombre"
    args_schema: Type[BaseModel] = DeleteClienteInput
    return_direct: bool = False
    _session: SessionProtocol = PrivateAttr()

    def __init__(self, session: SessionProtocol):
        super().__init__(session)

    def _run(self, nombre: str):
        try:
            LogToolMethod.log_initialization(self)
            manager: DataClienteManager = self._session.get_manager("clienteManager")
            cliente = self._get_cliente_by_name(nombre)
            manager.remove_item(cliente)
            return f"Cliente '{nombre}' eliminado correctamente del panel de contexto."
        except Exception as e:
            mensaje = f"Error eliminando el cliente '{nombre}' panel de contexto: {str(e)}"
            LogToolMethod.log_failure(self, mensaje)
            return mensaje
