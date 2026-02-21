"""
Elementos de contexto para el sistema de hipotecas.

Este módulo define las clases que representan los diferentes tipos de elementos
de contexto utilizados en el sistema de gestión de hipotecas. Proporciona una
jerarquía de clases para manejar información estructurada de clientes, gestores,
operaciones y recomendaciones hipotecarias.

Classes:
    - ContextItem: Clase abstracta base para todos los elementos de contexto
    - EzDataItem: Clase base para elementos de datos generales
    - EzHipotecaItem: Clase base para elementos relacionados con hipotecas
    - EzDataCliente: Información del cliente
    - EzDataGestor: Información del gestor
    - EzDataPreeval: Información de preevaluación
    - EzDataOperacion: Información de la operación
    - EzDataInterviniente: Información del interviniente
    - EzRecomendacionHipoteca: Recomendaciones de productos hipotecarios

Features:
    - Serialización JSON para persistencia
    - Formato específico para modelos de lenguaje (LLM)
    - Actualización segura de datos con validación de campos
    - Identificación única por tipo e ID
"""

import abc
import json
from typing import Dict, Any


class ContextItem(abc.ABC):
    """
    Clase para manejar los items del contexto
    """

    def __init__(
        self,
        name: str,
        id: str,
        data: dict,
        tab: str = "",
        llm_header: str = "",
    ):
        self.name = name
        self.id = id
        self.data = data
        self.tab = tab
        self.item_type = ""
        self.is_complete = False

    def get_id(self):
        return f"{self.id}"

    @abc.abstractmethod
    def get_llm_str(self):
        pass

    @abc.abstractmethod
    def to_json(self):
        pass


class EzDataItem(ContextItem):
    """
    Clase base para items de tipo EzData*.
    """

    def __init__(
        self,
        name: str,
        id: str,
        data: dict,
        item_type: str,
        tab: str = "",
        llm_header: str = "",
    ):
        super().__init__(name, id, data, tab)
        self.id = id
        self.data = data
        self.item_type = item_type
        self.llm_header = llm_header

    def get_llm_str(self):
        return f"## {self.name}\n{self.llm_header}:\n{json.dumps(self.data, indent=2, ensure_ascii=False)}"

    def to_json(self):
        return json.dumps(
            {
                "id": self.id,
                "name": self.name,
                "item_type": self.item_type,
                "tab": self.tab,
                "data": self.data,
                "llm_header": self.llm_header,
            },
            indent=2,
            ensure_ascii=False,
        )

    def get_data(self):
        return self.data

    def deep_update_node(self, node: dict, updates: dict):
        for key, value in updates.items():

            # 1) Si existe la clave y amos son dict -> actualización profunda
            if key in node and isinstance(node[key], dict) and isinstance(value, dict):
                self.deep_update_node(node[key], value)
                continue

            # 2) Si existe la clave pero no es dict -< sobreescribir
            if key in node:
                node[key] = value
                continue

            # 3) Si la clave no existe, buscamos en los sub-nodos
            updated_in_child = False
            for sub in node.values():
                if isinstance(sub, dict):
                    self.deep_update_node(sub, {key: value})
                    updated_in_child = True
                    break
            # 4) Si no se ha actualizado en ningún hijo, se crea en este nodo
            if not updated_in_child:
                node[key] = value

    def update(self, values: Dict[str, Any]):
        self.deep_update_node(self.data, values)


class EzHipotecaItem(ContextItem):
    """
    Clase base para items relacionados con hipotecas.
    """

    def __init__(
        self,
        name: str,
        id: str,
        data: dict,
        item_type: str,
        llm_header: str = "",
        tab: str = "",
    ):
        super().__init__(name, id, data, tab)
        self.id = id
        self.data = data
        self.item_type = item_type
        self.llm_header = llm_header or "Datos de hipoteca"

    def get_llm_str(self) -> str:
        return f"## {self.name}\n{self.llm_header}:\n{json.dumps(self.data, indent=2, ensure_ascii=False)}"

    def to_json(self) -> str:
        return json.dumps(
            {
                "id": self.id,
                "name": self.name,
                "item_type": self.item_type,
                "tab": self.tab,
                "data": self.data,
                "llm_header": self.llm_header,
            },
            indent=2,
            ensure_ascii=False,
        )

    def get_data(self) -> dict:
        return self.data


class EzRecomendacionHipoteca(EzHipotecaItem):
    """Item para los datos de la recomendación de hipotecas"""

    def __init__(self, name: str, id: str, data: dict, tab: str = ""):
        super().__init__(
            name,
            id,
            data,
            item_type="RecomendacionHipoteca",
            llm_header="Recomendación de hipoteca",
            tab=tab,
        )


class EzDataGestor(EzDataItem):
    """Item para los datos del gestor"""

    def __init__(self, name: str, id: str, data: dict, tab: str = ""):
        super().__init__(
            name,
            id,
            data,
            item_type="DataGestor",
            tab=tab,
            llm_header="Información del gestor",
        )


class EzDataCliente(EzDataItem):
    """Item para los datos del cliente"""

    def __init__(self, name: str, id: str, data: dict, tab: str = ""):
        super().__init__(
            name,
            id,
            data,
            item_type="DataCliente",
            tab=tab,
            llm_header="Información del cliente",
        )


class EzDataPreeval(EzDataItem):
    """Item para los datos de la preevaluación"""

    def __init__(self, name: str, id: str, data: dict, tab: str = ""):
        super().__init__(
            name,
            id,
            data,
            item_type="DataPreeval",
            tab=tab,
            llm_header="Información de la preevaluación",
        )


class EzDataOperacion(EzDataItem):
    """Item para los datos de la operación"""

    def __init__(self, name: str, id: str, data: dict, tab: str = ""):
        super().__init__(
            name,
            id,
            data,
            item_type="DataOperacion",
            tab=tab,
            llm_header="Información de la operación",
        )


class EzDataInterviniente(EzDataItem):
    """Item para los datos del interviniente"""

    def __init__(self, name: str, id: str, data: dict, tab: str = ""):
        super().__init__(
            name,
            id,
            data,
            item_type="DataInterviniente",
            tab=tab,
            llm_header="Información del interviniente",
        )


class EzDataMuestraInteres(EzDataItem):
    """Item para los datos de la muestra de interes"""

    def __init__(self, name: str, id: str, data: dict, tab: str = ""):
        super().__init__(
            name,
            id,
            data,
            item_type="DataMuestraInteres",
            tab=tab,
            llm_header="Información de la muestra de interes",
        )
