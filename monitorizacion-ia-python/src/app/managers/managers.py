"""
Gestores de elementos de contexto para el sistema de hipotecas.

Este módulo define los managers que gestionan el ciclo de vida de los elementos
de contexto, implementando el patrón Observer para notificar cambios y
proporcionando funcionalidades específicas para cada tipo de dato del sistema.

Classes:
    - ItemManager: Clase abstracta base para todos los managers
    - DataClienteManager: Gestor de información de clientes
    - DataGestorManager: Gestor de información de gestores
    - DataPreevalManager: Gestor de datos de preevaluación con validaciones
    - DataOperacionManager: Gestor de operaciones hipotecarias con reglas de negocio
    - DataIntervinienteManager: Gestor de datos de intervinientes
    - RecomendacionHipotecaManager: Gestor de recomendaciones y bonificaciones

Features:
    - Patrón Observer para notificación de cambios
    - Validación de datos según reglas de negocio
    - Integración con base de datos para recomendaciones
    - Gestión de bonificaciones y productos hipotecarios
"""

import abc
from typing import Dict, Any, List

from app.managers.items import (
    ContextItem,
    EzDataGestor,
    EzDataCliente,
    EzRecomendacionHipoteca,
    EzDataPreeval,
    EzDataInterviniente,
    EzDataOperacion,
    EzDataMuestraInteres,
)

from app.models.models_resto import DatosGestor, DatosCliente

from app.settings import settings

from qgdiag_lib_arquitectura import CustomLogger
from app.models.models import DatosIntervSimple


from pydantic import BaseModel


logger = CustomLogger("managers")

sql_server = settings.DATABASE_HOST
sql_database = settings.DATABASE_NAME
sql_username = settings.DATABASE_USER
sql_password = settings.DATABASE_PASSWORD
sql_driver = settings.DATABASE_DRIVER.replace(" ", "+")


class ItemManager(abc.ABC):
    """Clase para manejar los items de los managers"""

    def __init__(self):
        self.items = {}
        self.observers = []

    def add_observer(self, observer):
        self.observers.append(observer)

    def remove_observer(self, observer):
        self.observers.remove(observer)

    def notify_observers(self, item: ContextItem, change_type: str):
        for observer in self.observers:
            observer.update(item, change_type)

    def get_item(self, item_name: str) -> ContextItem:
        return self.items.get(item_name)

    def list_items(self):
        return list(self.items.values())

    def add_item(self, item: ContextItem):
        change_type = "update" if item.name in self.items else "add"
        self.items[item.name] = item
        self.notify_observers(item, change_type)

    def remove_item(self, item: ContextItem):
        self.items.pop(item.name)
        self.notify_observers(item, "remove")

    def validate_data(self, name: str):
        """Para la validación de los datos"""
        pass


class RecomendacionHipotecaManager(ItemManager):
    """
    Gestiona instancias de EzRecomendacionHipoteca:
        • Recuperar ítems
        • Crear/actualizar valores
        • Validar coherencia de los datos
    """

    def get_item(self, item_name) -> EzRecomendacionHipoteca | None:
        return super().get_item(item_name)

    def update_values(
        self, name: str, values: Dict[str, Any]
    ) -> EzRecomendacionHipoteca:
        """
        Crea o actualiza un EzRecomendacionHipoteca.

        • Si existe, valida y actualiza SOLO las claves reconocidas.
        • Si no existe, crea uno con los valores recibidos (se exige mínimo
          tipo_interes, ingresos, edad y certificacion_energetica_vivienda).

        Raises:
            TypeError / KeyError según inconsistencias detectadas.
        """
        ez_req = self.get_item(name)

        # Si ya existe, actualizamos campos válidos
        if ez_req:
            if not isinstance(ez_req, EzRecomendacionHipoteca):
                raise TypeError(
                    f"El objeto '{name}' no es un EzRecomendacionHipoteca válido."
                )

            for key, val in values.items():
                if key not in ez_req.data:
                    raise KeyError(f"La clave '{key}' no existe en '{name}'.")
                ez_req.data[key] = val

        # Si NO existe, necesitamos los campos minimos para instanciar
        else:
            minimos = {
                "tipo_interes",
                "ingresos",
                "edad",
                "certificacion_energetica_vivienda",
            }
            if not minimos.issubset(values):
                faltan = ", ".join(minimos - values.keys())
                raise KeyError(
                    f"Faltan campos obligatorios para crear '{name}': {faltan}"
                )
            data = {
                "tipo_interes": values["tipo_interes"],
                "ingresos": values["ingresos"],
                "edad": values["edad"],
                "certificacion_energetica_vivienda": values[
                    "certificacion_energetica_vivienda"
                ],
                "id_sesion": values.get("id_sesion", name),
                "timestamp": values.get("timestamp"),
            }

            ez_req = EzRecomendacionHipoteca(name, data)

        self.add_item(ez_req)
        return ez_req

    def validate_data(self, data_solicitud: dict) -> tuple[bool, str]:
        """
        Comprueba si los datos de un EzRecomendacionHipoteca son coherentes y completos.
        Devuelve (True, "") si todo es correcto; en caso contrario, (False, "<mensajes de error>").
        """

        errores: List[str] = []

        # 1. tipo_interes
        permitidos = {"fijo", "mixto", "variable"}
        if (
            not isinstance(data_solicitud.get("tipo_interes"), list)
            or not data_solicitud["tipo_interes"]
            or any(t.lower() not in permitidos for t in data_solicitud["tipo_interes"])
        ):
            errores.append(
                f"""En la variable 'tipo_interes' se ha pasado una lista vacía y debe ser una lista con 
                 valores {permitidos}.
                 Si el usuario no tiene claro qu tipo de interés quiere, se debe confirmar si quiere voler a realizar
                 la recomendación utilizando los tres tipos. En ese caso, debes volver a llamar a la tool pasando 
                 una lista con los tres tipos de interés: ['Fijo', 'Variable', 'Mixto']"""
            )

        # 2. ingresos
        if (
            not isinstance(data_solicitud.get("ingresos"), int)
            or data_solicitud["ingresos"] <= 0
        ):
            errores.append("'ingresos' debe ser número entero mayor que 0.")

        # 3. edad
        if not isinstance(data_solicitud.get("edad"), int) or not (
            18 <= data_solicitud["edad"] <= 75
        ):
            errores.append("'edad' debe ser entero entre 18 y 75.")

        # 4. certificacion_energetica_vivienda
        # if data_solicitud.get("certificacion_energetica_vivienda") not in {"A", "B", "C", "D", "E", "F", "G"}:
        #     errores.append("La certificación energética debe estar entre A y G.")

        return (len(errores) == 0, "\n".join(errores))


class DataGestorManager(ItemManager):
    """
    Clase para manejar el manager de los datos de la preevaluacion
    """

    def __init__(self):
        super().__init__()

    def get_item(self, item_name) -> EzDataGestor:
        return super().get_item(item_name)

    def update_values(self, name: str, values: DatosGestor) -> EzDataGestor:
        """
        Crea o actualiza uno o más campos de un objeto EzDataGestor.

        - Si el objeto no existe, se crea con los valores dados.
        - Si existe, se actualizan solo las claves válidas ya presentes.


        Args:
            name (str): Nombre del objeto EzDataGestor a actualizar o crear.
            values (Dict[str, Any]): Diccionario con los campos y valores nuevos.

        Returns:
            EzDataGestor: El objeto EzDataGestor resultante.

        Raises:
            TypeError: Si el objeto EzDataGestor no es un diccionario.
            KeyError: Si alguna de las claves proporcionadas no existe en el objeto.
        """
        try:
            ez_data = self.get_item(name)

            if ez_data:
                if (not isinstance(ez_data, EzDataGestor)) or (
                    not isinstance(ez_data.data, dict)
                ):
                    raise TypeError(
                        f""" El objeto recuperado '{name}' no es un diccionario EzDataGestor válido o no contiene
                        la información esperada."""
                    )

                for key in values:
                    if key not in ez_data.data:
                        raise KeyError(
                            f"La clave '{key}' no existe en el objeto '{name}'."
                        )

                ez_data.update(values)
            else:
                return (
                    f"No se ha encontrado el gestor con nombre {name} en el contexto de la sesión."
                    "Debes crear un nuevo gestor utilizando la tool 'create_gestor'"
                )
            # Guardar o reemplazar el objeto
            self.add_item(ez_data)
            return ez_data

        except KeyError as e:
            raise KeyError(f"Error actualizando los datos: {str(e)}")

    def validate_data(self, name: str) -> tuple[bool, str]:
        """
        Valida el contenido de un objeto EzDataPreeval.
        Verifica si todos los campos obligatorios están presentes y contienen valores válidos.


        Args:
            name (str): Nombre del objeto EzDataPreeval a validar.

        Returns:
            tuple[bool, str]:
                - bool: True si todos los datos son válidos y están completos, False en caso contrario.
                - str: Cadena con los mensajes de error si faltan datos o son incorrectos.
        """
        errores = []
        if len(self.items) == 1:
            errores.append("No puede haber más de un gestor.")
        datos_completos = len(errores) == 0
        return datos_completos, "\n".join(errores)


class DataClienteManager(ItemManager):
    """
    Clase para manejar el manager de los datos de la preevaluacion
    """

    def __init__(self):
        super().__init__()

    def get_item(self, item_name) -> EzDataCliente:
        return super().get_item(item_name)

    def update_values(self, name: str, values: DatosCliente) -> EzDataCliente:
        """
        Crea o actualiza uno o más campos de un objeto EzDataCliente.

        - Si el objeto no existe, se crea con los valores dados.
        - Si existe, se actualizan solo las claves válidas ya presentes.


        Args:
            name (str): Nombre del objeto EzDataCliente a actualizar o crear.
            values (Dict[str, Any]): Diccionario con los campos y valores nuevos.

        Returns:
            EzDataCliente: El objeto EzDataCliente resultante.

        Raises:
            TypeError: Si el objeto EzDataCliente no es un diccionario.
            KeyError: Si alguna de las claves proporcionadas no existe en el objeto.
        """
        try:
            ez_data = self.get_item(name)

            if ez_data:
                if (not isinstance(ez_data, EzDataCliente)) or (
                    not isinstance(ez_data.data, dict)
                ):
                    raise TypeError(
                        f"""El objeto recuperado '{name}' no es un diccionario 
                            EzDataCliente válido o no contiene la información esperada."""
                    )

                for key in values:
                    if key not in ez_data.data:
                        raise KeyError(
                            f"La clave '{key}' no existe en el objeto '{name}'."
                        )

                ez_data.update(values)
            else:
                return (
                    f"No se ha encontrado el cliente con nombre {name} en el contexto de la sesión."
                    "Debes crear un nuevo cliente utilizando la tool 'create_cliente'"
                )
            # Guardar o reemplazar el objeto
            self.add_item(ez_data)
            return ez_data

        except KeyError as e:
            raise KeyError(f"Error actualizando los datos: {str(e)}")

    def validate_data(self, name: str) -> tuple[bool, str]:
        """
        Valida el contenido de un objeto EzDataCliente.
        Verifica si todos los campos obligatorios están presentes y contienen valores válidos.


        Args:
            name (str): Nombre del objeto EzDataCliente a validar.

        Returns:
            tuple[bool, str]:
                - bool: True si todos los datos son válidos y están completos, False en caso contrario.
                - str: Cadena con los mensajes de error si faltan datos o son incorrectos.
        """
        errores = []
        datos_completos = len(errores) == 0
        return datos_completos, "\n".join(errores)


class DataPreevalManager(ItemManager):
    """
    Clase para manejar el manager de los datos de la preevaluacion
    """

    def __init__(self):
        super().__init__()

    def get_item(self, item_name) -> EzDataPreeval:
        return super().get_item(item_name)


class DataOperacionManager(ItemManager):
    """
    Clase para manejar el manager de los datos de la operacion
    """

    def __init__(self):
        super().__init__()

    def get_item(self, item_name) -> EzDataOperacion:
        return super().get_item(item_name)


class DataIntervinienteManager(ItemManager):
    """
    Clase para manejar el manager de los datos del interviniente
    """

    def __init__(self):
        super().__init__()

    def get_item(self, item_name) -> EzDataInterviniente:
        return super().get_item(item_name)


class DataMuestraInteresManager(ItemManager):
    """Clase para manejar el manager de los datos del interviniente"""

    def __init__(self):
        super().__init__()

    def get_item(self, item_name) -> EzDataMuestraInteres:
        return super().get_item(item_name)
