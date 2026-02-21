"""
Herramientas de LangChain para gestión y recomendación de productos hipotecarios.

Incluye tools para crear, eliminar, consultar productos, negociar bonificaciones y consultar promociones
activas de hipotecas.
"""

from typing import Type
import json
import uuid
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field, PrivateAttr
from typing import List, Optional, Union
import pandas as pd

from app.managers.session_adapter import SessionProtocol
from app.managers.items import (
    EzRecomendacionHipoteca,
)

from app.managers.managers import RecomendacionHipotecaManager


from app.repositories.sqlserver.session_data_dao import DataSession
from app.models.models import ParametrosRecomendadorHipotecas
from app.services.bonificaciones_service import BonificacionesService

from app.services.data import logica_recomendador_hipotecas
from app.repositories.sqlserver.database_connector import get_manual_db_session
from sqlalchemy.exc import SQLAlchemyError
from app.models.models_fichas import FichaProductoHipoteca

IDENTIFICADOR_SESION = "Identificador de sesión (UUID)."

from app.services.tools_logger import LogToolMethod


#####################################################################################################
################################# TOOLS RECOMENDACIÓN HIPOTECAS #####################################
#####################################################################################################
class EzRecomendacionHipotecaBaseTool(BaseTool):
    """Clase base para herramientas de recomendación de hipotecas"""

    name: str = "hipoteca_base_tool"
    description: str = (
        "Herramienta base para hipotecas. No debe ser usada directamente."
    )

    _session: SessionProtocol = PrivateAttr()

    def __init__(self, session: SessionProtocol):
        super().__init__()
        self._session = session

    def _get_hipoteca_by_nombre(self, nombre: str) -> EzRecomendacionHipoteca:
        manager = self._session.get_manager("recomendacionHipotecaManager")
        return manager.get_item(nombre)

    def _register_request(self, request: EzRecomendacionHipoteca) -> None:
        self._session.get_manager("recomendacionHipotecaManager").add_item(request)

    def _run(self, *args, **kwargs):
        """Implementación dummy para tests, no debe usarse en producción"""
        raise NotImplementedError(
            "EzRecomendacionHipotecaBaseTool no debe ejecutarse directamente."
        )


# ---------------- TOOL PARA CREAR / REGISTRAR UNA RECOMENDACION DE HIPOTECAS ---------------- #


class CreateRecomendacionHipotecaInput(BaseModel):
    """
    Esquema de entrada para crear y añadir una operación al panel de contexto.
    Contiene el nombre de la operación y los datos validados.
    """

    nombre: str = Field(
        description="""Nombre que recibirá el objeto EzDade datos con la recomendación. Se debe utilizar
    un nombre amigable como 'Recomendación 1' e incrementar el número si se crean más"""
    )
    datos: ParametrosRecomendadorHipotecas = Field(
        description="Objeto con los datos validados de la recomendación que se debe almacenar en el panel de contexto."
    )


class CreateRecomendacionHipotecaTool(EzRecomendacionHipotecaBaseTool):
    """
    Recomienda las hipotecas que pueden interesar al cliente en función de sus preferencias y características.
    Sólo debe invocarse para recomendar hipotecas según preferencias del cliente de tipo de interés (fijo, mixto,
    variable), ingresos, edad, certificación energética y si la vivienda es propiedad de Unicaja.
    Para otras consultas de los productos de hipoteca no se debe utilizar.
    Devuelve la información completa de las hipotecas que cumplen los requisitos.
    """

    name: str = "create_recomendacion_hipoteca"
    description: str = (
        "Genera una recomendación de 3 hipotecas basada en las preferencias del usuario."
        "Almacena los datos de una recomendación identificada por 'nombre' en el panel de contexo."
    )
    args_schema: Type[BaseModel] = CreateRecomendacionHipotecaInput
    return_direct: bool = False
    _session: SessionProtocol = PrivateAttr()
    _tipos_interes = {"mixto": 3, "fijo": 1, "variable": 1}

    def _run(self, nombre: str, datos: ParametrosRecomendadorHipotecas) -> dict | str:
        try:
            LogToolMethod.log_initialization(self)

            manager: RecomendacionHipotecaManager = self._session.get_manager(
                "recomendacionHipotecaManager"
            )
            resultado_recomendacion = None

            if nombre in manager.items:
                return "Ya existe una recomendación con el mismo nombre en el panel de contexto. "

            # Genera un identificacdor un UUID único para el nombre del item.
            id = str(uuid.uuid4())

            # Crear EzDataPreeval en memoria
            datos_dict = datos.model_dump()
            item_recomendacion = EzRecomendacionHipoteca(nombre, id, datos_dict)

            datos_recomendacion = ParametrosRecomendadorHipotecas(
                **item_recomendacion.data
            )

            errores_inputs = datos_recomendacion.validar_inputs()

            if errores_inputs != "":
                error_message = f"""Se han producido los siguientes errores al invocar
                'recomendar_hipotecas':{errores_inputs}"""
                return {"error": error_message}

            else:
                resultado_recomendacion = self.recomendar_hipotecas(datos_recomendacion)

        except Exception as e:
            # Capturamos cualquier excepción inesperada
            mensaje = {"error": f"Error inesperado al generar recomendación: {str(e)}"}
            LogToolMethod.log_failure(self, mensaje)
            return mensaje 

        # Evaluamos el resultado
        if resultado_recomendacion is None:
            return {
                "error": (
                    "No se han encontrado productos compatibles con los criterios establecidos. "
                    "Compruebe los datos de entrada e inténtelo de nuevo."
                )
            }
        else:
            datos_dict["resultado_recomendacion"] = resultado_recomendacion
            item_recomendacion = EzRecomendacionHipoteca(nombre, id, datos_dict)
            manager.add_item(item_recomendacion)
            return {
                "recomendacion_generada": True,
                "recomendacion_guardada": resultado_recomendacion,
            }

    def _cargar_productos_por_codigo(
        self, codigos_administrativos: List[str]
    ) -> Optional[List[dict]]:
        """
        Carga y devuelve los productos de hipoteca en formato dict para los códigos indicados.
        Devuelve None si algún código no existe. Lanza SQLAlchemyError si la consulta falla.
        """
        db_session = get_manual_db_session()
        productos_recomendados: List[dict] = []

        try:
            for codigo in codigos_administrativos:
                producto = (
                    db_session.query(FichaProductoHipoteca)
                    .filter_by(COD_ID_PROD_HIPO=codigo)
                    .first()
                )

                if producto is None:
                    # Cerrar sesión antes de salir por None
                    db_session.close()
                    return None

                producto_dict = json.loads(producto.DES_JSON)
                productos_recomendados.append(producto_dict)

            return productos_recomendados

        except SQLAlchemyError as e:
            db_session.rollback()
            # Opcional: añade el código en el mensaje para diagnóstico
            raise SQLAlchemyError(f"Error consultando producto {codigo}: {str(e)}")

        finally:
            # Asegura cierre aunque no haya excepciones
            db_session.close()

    def _filtrar_certificacion(self, df: pd.DataFrame, cert: str) -> pd.DataFrame:
        """Filtra por certificación energética A/B o por 'sin certificación'."""
        if cert in {"A", "B"}:
            return df[df["certificacion_energetica"].str.contains(cert, na=False)]
        return df[
            df["certificacion_energetica"].isna()
            | (df["certificacion_energetica"].str.strip() == "")
        ]

    def _filtrar_ingresos_edad(
        self, df_t: pd.DataFrame, ingresos: int, edad: int
    ) -> pd.DataFrame:
        """Aplica filtros por ingresos y, si procede, por edad."""
        if ingresos >= 2000:
            return df_t[df_t["ingresos_minimos"] <= ingresos]
        mask = (df_t["edad_maxima_primera_residencia"] >= edad) & (
            df_t["ingresos_minimos"] <= ingresos
        )
        return df_t[mask]

    def _seleccionar_recs(
        self, df: pd.DataFrame, tipos: list[str], ingresos: int, edad: int
    ) -> pd.DataFrame:
        """Ordena por 'valor' y devuelve top por tipo (3 mixtas, 1 fijo, 1 variable), acotado a top 3 final."""
        recs = []
        for t in tipos:
            df_t = self._filtrar_ingresos_edad(
                df[df["tipo_interes"] == t], ingresos, edad
            )
            n = self._tipos_interes.get(t, 0)
            if n:
                recs.append(df_t.sort_values("valor").head(n))
        if not recs:
            return pd.DataFrame(columns=df.columns)
        return pd.concat(recs).sort_values("valor").reset_index(drop=True).head(3)

    def recomendar_hipotecas(
        self, data_solicitud: ParametrosRecomendadorHipotecas
    ) -> Optional[Union[List[dict], dict]]:
        """
        Devuelve una lista de dict de hipotecas recomendadas o un dict con 'resultado' si no hay compatibilidad.
        """
        df = pd.DataFrame(logica_recomendador_hipotecas.hipotecas)

        ingresos = data_solicitud.ingresos
        edad = data_solicitud.edad
        cert = data_solicitud.certificacion_energetica_vivienda

        propiedad = data_solicitud.vivienda_propiedad_unicaja

        if propiedad.upper() == "S":
            recomendaciones = df[df["vivienda_propiedad_unicaja"] == "S"].reset_index(
                drop=True
            )
        else:
            df_n = df[df["vivienda_propiedad_unicaja"] == "N"]
            df_n = self._filtrar_certificacion(df_n, cert)

            tipos = [s.lower() for s in data_solicitud.tipo_interes]
            df_n = df_n[df_n["tipo_interes"].isin(tipos)]

            recomendaciones = self._seleccionar_recs(df_n, tipos, ingresos, edad)

        codigos = recomendaciones["codigo_administrativo"].tolist()
        productos_recomendados = self._cargar_productos_por_codigo(codigos)

        if productos_recomendados is None:
            return None  # alguno de los códigos no existe

        if not productos_recomendados:
            return {
                "resultado": (
                    "No se han encontrado productos compatibles con los criterios establecidos."
                    "Compruebe los datos de entrada e inténtelo de nuevo."
                )
            }

        return productos_recomendados


# ---------------- TOOL PARA ELIMINAR UNA RECOMENDACIÓN DE HIPOTECA ---------------- #
class DeleteRecomendacionHipotecaInput(BaseModel):
    """
    Esquema de entrada para eliminar una recomendación de hipoteca del panel de contexto.
    Requiere el nombre de la recomendación.
    """

    nombre: str = Field(
        description="Nombre de la recomendación de hipoteca a eliminar."
    )


class DeleteRecomendacionHipotecaTool(EzRecomendacionHipotecaBaseTool):
    """
    Herramienta que elimina una recomendación de hipoteca del  panel de contexto a partir de su nombre.
    """

    name: str = "delete_recomendacion_hipoteca"
    description: str = "Elimina una recomendacion de hipoteca dado su nombre y sesión."
    args_schema: Type[BaseModel] = DeleteRecomendacionHipotecaInput
    return_direct: bool = False
    _session: SessionProtocol = PrivateAttr()

    def __init__(self, session: SessionProtocol):
        super().__init__(session)

    def _run(self, nombre: str):
        try:
            LogToolMethod.log_initialization(self)

            manager: RecomendacionHipotecaManager = self._session.get_manager(
                "recomendacionHipotecaManager"
            )
            recomendacion = self._get_hipoteca_by_nombre(nombre)
            manager.remove_item(recomendacion)
            return f"Recomendacion de hipoteca '{nombre}' eliminada correctamente del panel de contexto."
        except Exception as e:
            mensaje = {
                "error": f"Error eliminando la recomendacion de hipoteca del panel de contexto: {str(e)}"
            }
            LogToolMethod.log_failure(self, mensaje)
            return mensaje


# TOOL PARA CONSULTAR UN PRODUCTO
class ConsultarProductoInput(BaseModel):
    """
    Modelo de entrada para la herramienta `consultar_producto`.

    Atributos:
        codigo_administrativo (str): Código administrativo del producto hipotecario.
                                     Debe tener 6 dígitos y empezar por '050'.
    """

    codigo_administrativo: str = Field(
        description="""Código administrativo del producto hipotecario. Está formado por el producto (3 digitos='050') 
        seguido del subproducto (otros 3 digitos). Siempre deben ser 6 digitos que empiezan por '050'.
        """
    )


class ConsultarProductoTool(EzRecomendacionHipotecaBaseTool):
    """
    Herramienta para consultar la información concreta sobre un producto hipotecario.

    Hereda de `EzRecomendacionHipotecaBaseTool` y permite acceder al catálogo de productos para devolver
    la información de producto asociada a un código administrativo.
    """

    name: str = "consultar_producto"
    description: str = (
        "Devuelve la información de un producto hipotecario consultando el catálogo según el código administrativo."
    )
    args_schema: Type[BaseModel] = ConsultarProductoInput
    return_direct: bool = False
    _session: SessionProtocol = PrivateAttr()

    def __init__(self, session: SessionProtocol):
        """
        Inicializa la herramienta `consultar_producto`.

        Args:
            session (SessionProtocol): Objeto de sesión para gestionar dependencias.
        """
        super().__init__(session)

    def _run(
        self,
        codigo_administrativo: str,
    ) -> dict:
        """
        Ejecuta la consulta de un producto disponibles en el catálogo.

        Args:
            codigo_administrativo (str): Código administrativo del producto hipotecario.

        Returns:
            dict: Un diccionario con toda la información del producto.
            En caso de error devuelve:
                {
                    "error": <mensaje de error>,
                }
        """
        try:
            LogToolMethod.log_initialization(self)

            # Validacion del codigo administrativo
            codigo_administrativo = str(codigo_administrativo).zfill(6)
            if codigo_administrativo == "050":
                return {
                    "codigo_administrativo": codigo_administrativo,
                    "mensaje": (
                        "No se ha faciltiado un producto específico, solo se indicó '050'."
                        "Debes pedir al usuario el codigo completo o realizar una recomendación."
                    ),
                }
            if not codigo_administrativo.isdigit() or len(codigo_administrativo) != 6:
                return {
                    "error": "El código administrativo debe contener exactamente 6 dígitos numércios.",
                    "codigo_administrativo": codigo_administrativo,
                }
            # Creamos sesión de base de datos
            db_session = DataSession()

            # Usamos el método listar_productos con filtro por código administrativo
            productos = db_session.listar_productos(
                codigo_administrativo=codigo_administrativo
            )
            if not productos:
                return {
                    "error": f"No se encontró producto con código {codigo_administrativo}"
                }

            producto_dict = json.loads(productos[0].DES_JSON)

            return {
                "codigo_administrativo": codigo_administrativo,
                "informacion_producto": producto_dict,
            }

        except Exception as e:
            mensaje = {
                "error": f"Error al consultar la información del producto: {str(e)}",
            }
            LogToolMethod.log_failure(self, mensaje)
            return mensaje 


# TOOL PARA NEGOCIAR BONIFICACIONES
class NegociarBonificacionesInput(BaseModel):
    """
    Modelo de entrada para la herramienta `negociar_bonificaciones`.

    Atributos:
        codigo_administrativo (str): Código administrativo del producto hipotecario.
                                     Debe tener 6 dígitos y empezar por '050'.
    """

    codigo_administrativo: str = Field(
        description="Código administrativo del producto para el que se quieren negociar las bonificaciones."
    )


class NegociarBonificacionesTool(EzRecomendacionHipotecaBaseTool):
    """Herramienta para negociar bonificaciones"""

    name: str = "negociar_bonificaciones"
    description: str = (
        "Permite conocer y negociar bonificaciones de un producto hipotecario utilizando su código administrativo."
        "Devuelve un JSON con las bonificaciones disponibles y su impacto en puntos porcentuales."
    )
    args_schema: Type[BaseModel] = NegociarBonificacionesInput
    return_direct: bool = False
    _session: SessionProtocol = PrivateAttr()

    def __init__(self, session: SessionProtocol):
        super().__init__(session)

    def _run(
        self,
        codigo_administrativo: str,
    ) -> dict:
        try:
            LogToolMethod.log_initialization(self)

            # Validacion del codigo administrativo
            codigo_administrativo = str(codigo_administrativo).zfill(6)
            if codigo_administrativo == "050":
                return {
                    "codigo_administrativo": codigo_administrativo,
                    "mensaje": (
                        "No se ha faciltiado un producto específico, solo se indicó '050'."
                        "Debes pedir al usuario el codigo completo o realizar una recomendación."
                    ),
                }
            if not codigo_administrativo.isdigit() or len(codigo_administrativo) != 6:
                return {
                    "error": "El código administrativo debe contener exactamente 6 dígitos numércios.",
                    "codigo_administrativo": codigo_administrativo,
                }

            # Partir el código administrativo
            producto_ent = codigo_administrativo[:3]
            subpro_ent = codigo_administrativo[3:]
            headers = self._session.get_context().headers
            service = BonificacionesService(headers=headers)
            body = {
                "PBC-ENTRADA-ICP": {
                    "PBC-PRODUCTO-ENT": producto_ent,
                    "PBC-SUBPRO-ENT": subpro_ent,
                }
            }

            resultado = service.call(body)
            dict_resultados = self._parse_bonificaciones(resultado)

            return dict_resultados

        except Exception as e:
            mensaje = {"error": f"Error al consultar las bonificaciones: {str(e)}"}
            LogToolMethod.log_failure(self, mensaje)
            return mensaje

    @staticmethod
    def _parse_condiciones(condiciones: list) -> list[dict]:
        condiciones_validas = []
        for cond in condiciones:
            id_cond = cond.get("PBC-ID-CONDICION", "").strip()
            if not id_cond:
                continue

            desc = cond.get("PBC-DESC-CONDICION", {})
            texto = " ".join(v.strip() for v in desc.values() if v and v.strip())
            if not texto:
                continue

            condiciones_validas.append(
                {"id_condicion": id_cond, "detalle_condicion": texto}
            )
        return condiciones_validas

    @staticmethod
    def _parse_bloques(bloques: list) -> list[dict]:
        bloques_validos = []
        for bloque in bloques:
            id_bloque = bloque.get("PBC-ID-BLOQUE", "").strip()
            if not id_bloque:
                continue

            bonif_bloque = bloque.get("PBC-BONIF-BLOQUE")
            condiciones_validas = NegociarBonificacionesTool._parse_condiciones(
                bloque.get("PBC-CONDICIONES-ICP", [])
            )

            bloques_validos.append(
                {
                    "id_bloque": id_bloque,
                    "bonificacion_bloque": bonif_bloque,
                    "condiciones": condiciones_validas,
                }
            )
        return bloques_validos

    @staticmethod
    def _parse_bonificaciones(resultado: dict) -> dict:
        salida = resultado["response"]["PBC-SALIDA-ICP"]
        campanya = salida["PBC-DATOS-CAMPANYA-ICP"]

        conceptos = campanya["PBC-CONCEPTOS-ICP"]

        concepto_valido = next(
            (c for c in conceptos if c.get("PBC-ID-CONCEPTO", "").strip()), None
        )
        if not concepto_valido:
            return {}

        id_concepto = concepto_valido["PBC-ID-CONCEPTO"]
        bonif_max = concepto_valido.get("PBC-BONIF-MAX")
        bloques_validos = NegociarBonificacionesTool._parse_bloques(
            concepto_valido.get("PBC-BLOQUES-ICP", [])
        )

        return {
            "id_concepto": id_concepto,
            "bonificacion_total_maxima": bonif_max,
            "bloques": bloques_validos,
        }


# TOOL PARA CONSULTAR CAMPAÑAS/PROMOCIONES ACTIVAS
class ConsultarPromocionInput(BaseModel):
    """
    Modelo de entrada para la herramienta `consultar_promociones`.

    """


class ConsultarPromocionTool(EzRecomendacionHipotecaBaseTool):
    """
    Herramienta para consultar las promociones o campañas disponibles y activas en el momento de la contratación de
    una hipoteca.

    Hereda de `EzRecomendacionHipotecaBaseTool` y permite acceder al catálogo de campañas para devolver
    las promociones disponibles en el momento de la contratación de la hipoteca.
    """

    name: str = "consultar_promociones"
    description: str = "Devuelve la lista de promociones disponibles y activas."
    args_schema: Type[BaseModel] = ConsultarPromocionInput
    return_direct: bool = False
    _session: SessionProtocol = PrivateAttr()

    def __init__(self, session: SessionProtocol):
        """
        Inicializa la herramienta `consultar_promocion`.

        Args:
            session (SessionProtocol): Objeto de sesión para gestionar dependencias.
        """
        super().__init__(session)

    def _run(
        self,
    ) -> dict:
        """
        Ejecuta la consulta de las promociones disponibles y activas.

        Returns:
            dict: Un diccionario con toda la información de las promociones.
            En caso de error devuelve:
                {
                    "error": <mensaje de error>,
                }
        """
        try:
            LogToolMethod.log_initialization(self)

            db_session = DataSession()
            promociones = db_session.get_campanyas()
            return {
                "Promociones aplicables a la contratación de este producto": promociones,
            }

        except Exception as e:
            mensaje = {
                "error": f"Error al consultar las promociones vigentes: {str(e)}",
            }
            LogToolMethod.log_failure(self, mensaje)
            return mensaje 


#####################################################################################################
############################# TOOL PARA CATALOGO DE PRODUCTOS #######################################
#####################################################################################################


class ObtenerCatalogoProductosInput(BaseModel):
    """
    Modelo de entrada para la herramienta `consultar_catalogo_hipotecas`.
    No requiere parámetros de entrada actualmente.
    """

    pass


class HipotecaInfo(BaseModel):
    """Modelo de datos para la información de una hipoteca"""

    nombre: str
    tipo_interes: str
    codigo_comercial: str
    codigo_administrativo: str


class ObtenerCatalogoProductosTool(EzRecomendacionHipotecaBaseTool):
    """
    Herramienta para consultar el catálogo de hipotecas disponibles.
    Hereda de `EzRecomendacionHipotecaBaseTool` y devuelve los productos con los campos relevantes
    para el agente: nombre, tipo de interés, código comercial y código administrativo.
    """

    name: str = "obtener_catalogo_hipotecas"
    description: str = (
        "Devuelve el catálogo de hipotecas con nombre, tipo de interés y códigos."
    )
    args_schema: Type[BaseModel] = ObtenerCatalogoProductosInput
    return_direct: bool = False
    _session: SessionProtocol = PrivateAttr()

    def __init__(self, session: SessionProtocol):
        super().__init__(session)

    def _run(self) -> dict:
        """
        Ejecuta la consulta del catálogo de hipotecas.

        Returns:
            dict: Diccionario con la lista de hipotecas resumida, o error en caso de fallo.
        """
        try:
            LogToolMethod.log_initialization(self)

            resultado: List[HipotecaInfo] = [
                HipotecaInfo(
                    nombre=h["nombre"],
                    tipo_interes=h["tipo_interes"],
                    codigo_comercial=h["codigo_comercial"],
                    codigo_administrativo=h["codigo_administrativo"],
                )
                for h in logica_recomendador_hipotecas.hipotecas
            ]
            return {"hipotecas": [r.dict() for r in resultado]}
        except Exception as e:
            mensaje = {"error": str(e)}
            LogToolMethod.log_failure(self, mensaje)
            return mensaje
