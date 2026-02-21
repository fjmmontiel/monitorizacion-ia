"""
Gestión de contexto para el sistema de hipotecas.

Este módulo proporciona las clases necesarias para gestionar el contexto de una sesión
de conversación, incluyendo elementos de contexto, registro de llamadas a herramientas
y salidas de conversación. Permite el seguimiento y formateo de la información contextual
utilizada durante las interacciones del sistema.

Classes:
    - Context: Clase principal para manejar el contexto de la sesión
    - ToolCall: Modelo para representar llamadas a herramientas
    - ToolCallLog: Gestor de registro de llamadas a herramientas
    - ToolCallFormatter: Utilidad para formatear llamadas a herramientas

Note:
    Antes se utilizaba SessionSingleton, pero ha quedado obsoleto. Ahora se usan DistributedContext y
    DistributedSessionManager para nuevas implementaciones.
"""

from app.managers.items import ContextItem
import json

from typing import List, Any, Dict
from pydantic import BaseModel, Field
from qgdiag_lib_arquitectura import CustomLogger

logger = CustomLogger("Contexto.")


class ToolCallFormatter:
    """
    Clase para manejar el formato de la llamada
    """

    @staticmethod
    def format(tool_call: "ToolCall"):
        """
        Formatea la llamada a una herramienta de modo que pueda ser reproducida como código Python válido.

        Args:
            tool_call (ToolCall): Contiene la información de la herramienta ejecutada.

        Returns:
            str: Una cadena formateada como código Python.
        """
        tool_name = tool_call.tool_name
        tool_input = tool_call.params

        # Convertir los parámetros de entrada a una representación en argumentos de función
        input_args = ", ".join(
            f"{key}={repr(value)}" for key, value in tool_input.items()
        )

        # Generar el código como una string multilinea
        formatted_call = f"{tool_name}({input_args})\n"
        return formatted_call


class ToolCall(BaseModel):
    """
    Clase para manejar la llamada
    """

    tool_name: str = Field(description="The name of the tool that has been called")
    params: Dict[str, Any] = Field(description="Parameters received")
    successful: bool = Field(
        description="Boolean indicating if the tool call was successful or not"
    )
    result: Any = Field(description="Result of the tool call")
    formatted_call: str = Field(
        description="""Formatted call for presentation in a 
                                logging system. It should not be set manually;
                                 it updates automatically when the object 
                                is initialized""",
        default=None,
    )

    def __init__(self, **data):
        super().__init__(**data)
        # Logic to format `formatted_call`
        self.formatted_call = ToolCallFormatter.format(self)


class ToolCallLog:
    """
    Clase para manejar el log de la llamada
    """

    def __init__(self):
        self._tool_call_list: List[ToolCall] = []

    def add(self, tool_call: ToolCall) -> None:
        self._tool_call_list.append(tool_call)

    def to_string(self) -> str:
        return "\n".join(
            ToolCallFormatter.format(tool_call) for tool_call in self._tool_call_list
        )

    def to_json(self) -> List:
        result = []
        for tool_call in self._tool_call_list:
            json_str = tool_call.json()
            json_result = json.loads(json_str)
            result.append(json_result)
        return result


class Context:
    """
    Clase para manejar el contexto
    """

    def __init__(self):
        self.items = {}
        self.tool_call_log = ToolCallLog()
        self.conversation_outputs = []

    def _put_item(self, item: ContextItem) -> None:
        self.items[item.get_id()] = item

    def _remove_item(self, item: ContextItem) -> None:
        self.items.pop(item.get_id())

    def update(self, item: ContextItem, change_type: str):
        """
        Method called by the observable to notify changes to an item.

        Args:
        - item (ContextItem): The item that was modified.
        - change_type (str): The type of change performed (e.g., "add", "update", "remove").

        Raises:
        - ValueError: If the change_type is not one of "add", "update", or "remove".
        """

        if change_type == "add":
            self.add_conversation_output(f"[ADD_CONTEXT={item.get_id()}]")
            self._put_item(item)
        elif change_type == "update":
            self.add_conversation_output(f"[UPDATE_CONTEXT={item.get_id()}]")
            self._put_item(item)
        elif change_type == "remove":
            self.add_conversation_output(f"[REMOVE_CONTEXT={item.get_id()}]")
            self._remove_item(item)
        else:
            raise ValueError(
                "Unsupported notify operation. Use 'add', 'update', or 'remove'."
            )

    def get_item(self, id: str) -> ContextItem:
        return self.items[id]

    def get_llm_str(self) -> str:
        """
        Generates a concatenated string of all the `get_llm_str` outputs from the ContextItems in the context.

        Returns:
        - str: A single string containing all the concatenated `get_llm_str` results from the items.
        """
        all_items = []

        for item in self.items.values():
            # Verificar que el item tenga el método get_llm_str
            if not hasattr(item, "get_llm_str"):
                raise AttributeError(
                    f"El item '{item.name}' de tipo '{item.item_type}' no tiene método get_llm_str."
                )

            # Convertir el item a LLM string
            item_llm_str = item.get_llm_str()

            all_items.append(item_llm_str)

        items_str = "\n".join(all_items)
        tool_call_str = self.get_tool_call_str()
        return f"{items_str}\n\n# TOOL CALL LOG \n{tool_call_str}"

    def to_json(self):
        # Recolectar todos los items en una sola lista
        all_items = []

        for item in self.items.values():
            # Verificar que el item tenga el método to_json
            if not hasattr(item, "to_json"):
                raise AttributeError(
                    f"El item '{item.name}' de tipo '{item.item_type}' no tiene método to_json."
                )

            # Convertir el item a JSON
            item_json_str = item.to_json()
            item_json = json.loads(item_json_str)

            all_items.append(item_json)

        tool_call_log = self.tool_call_log.to_json()

        data = {"items": all_items, "tool_call_log": tool_call_log}

        return json.dumps(data)

    def get_tool_call_json(self) -> str:
        data = {"tool_call_log": self.tool_call_log.to_json()}
        return json.dumps(data)

    def add_conversation_output(self, output: str) -> None:
        self.conversation_outputs.append(output)

    def pop_convertation_output_element(self):
        element = self.conversation_outputs.pop(0)
        return element

    def conversation_output_is_empty(self):
        return len(self.conversation_outputs) == 0

    def conversation_output_is_not_empty(self):
        return len(self.conversation_outputs) > 0

    def add_tool_call(self, tool_call: ToolCall) -> None:
        self.tool_call_log.add(tool_call)

    def get_tool_call_str(self) -> str:
        return self.tool_call_log.to_string()
