"""
Servicios de procesamiento de fichas de productos, campañas y bonificaciones.

Proporciona funcionalidad para extraer, procesar y almacenar información
de documentos PDF, archivos Excel y datos de productos hipotecarios
utilizando IA para estructuración automática de contenido.
"""

import os
import json
from docx2pdf import convert
from pathlib import Path
import httpx as httpx
import pandas as pd
import re
import asyncio
import shutil
from datetime import datetime
from pydantic import BaseModel, Field


from openai import OpenAI
import instructor
from typing import List, Dict

from sqlalchemy.exc import SQLAlchemyError

from langchain_community.document_loaders import PyPDFLoader

from qgdiag_lib_arquitectura.utilities.ai_core.control_gastos import (
    alogging_gastos_event_hooks,
    amake_check_blocked_event_hooks,
)
from qgdiag_lib_arquitectura import CustomLogger
from qgdiag_lib_arquitectura.utilities.ai_core.ai_core import get_ai_core_session


from app.exceptions.app_exceptions import RepositoryException
from app.models.models_fichas import (
    FichaProducto,
    FichaCampania,
    FichaProductoHipoteca,
    FichaCampanyasHipotecas,
    FichaTraducciones,
    ProductoTiposInteres,
)
from app.settings import settings


logger = CustomLogger("hipotecas_process_service")


# Cargar variables de entorno para conectar AI Core
AICORE_URL = settings.AICORE_URL
ENGINE_ID = settings.ENGINE_ID


# Leer el contenido del PDF usando PyPDFLoader
def leer_pdf(ruta_pdf: str | Path) -> str:
    """
    Funcion para leer pdfs
    """
    loader = PyPDFLoader(ruta_pdf)
    pages = loader.load()
    return (
        "\n".join([page.page_content for page in pages])
        or "El documento está vacío o no contiene texto legible."
    )


async def conexion_modelo(headers: Dict[str, str]):
    """
    Funcion para conectar con el modelo
    """

    access_key, secret_key, server_cookies = await get_ai_core_session(headers)
    hooks = {
        "request": [await amake_check_blocked_event_hooks(headers=headers)],
        "response": [alogging_gastos_event_hooks],
    }

    http_client = httpx.Client(event_hooks=hooks)
    http_client.cookies = server_cookies

    api_key = access_key + ":" + secret_key
    client = OpenAI(
        api_key=api_key, base_url=AICORE_URL + "/model/openai", http_client=http_client
    )
    client = instructor.from_openai(client, mode=instructor.Mode.JSON)
    return client


def conversion_doc_pdf(docx_path: str | Path):
    """
    Funcion para convertir un doc en pdf
    """
    try:
        # Ruta de salida (PDF con el mismo nombre)
        docx_path = Path(docx_path)
        output_pdf_path = docx_path.with_suffix(".pdf")
        convert(docx_path, output_pdf_path)
        logger.info(f"PDF generado correctamente en:\n{output_pdf_path}")
        return output_pdf_path
    except Exception as e:
        logger.info(f"Error al convertir el archivo: {e}")
        return False


class LecturaFichaProductoService:
    """
    Servicio para procesamiento automático de fichas de productos hipotecarios.

    Extrae información estructurada de documentos PDF mediante IA y almacena
    los datos procesados en base de datos con gestión de archivos históricos.
    """

    _instance = None

    def __init__(self, headers, db_session):
        """
        Inicializa el DAO con una sesión de base de datos ya creada.

        Args:
            db_session: Instancia de sesión de SQLAlchemy para usar.
        """
        self.db_session = db_session
        self.headers = headers

    def procesar_tipos_interes(self, pdf_path, cliente):

        contenido_pdf = leer_pdf(pdf_path)

        # Llamada al modelo de AI Core
        logger.info("Creando conexión con el modelo de AI Core.")
        respuesta = cliente.chat.completions.create(
            model=ENGINE_ID,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Eres un experto en extraer información estructurada de fichas de productos bancarios. "
                        "Devuelve exclusivamente un JSON válido (sin texto adicional) que cumpla el esquema solicitado."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        """Objetivo: extrae del documento PDF los tipos de interés (porcentajes) de cada 
                    producto hipotecario.\n\n"""
                        "Campos de referencia en el PDF:\n"
                        "- PROD: código de producto (ej. 12345)\n"
                        "- SUBP: código de subproducto (ej. 01)\n"
                        "- PROD. COM: código comercial (ej. ABC123)\n"
                        "- Grupos de interés: 'GRUPO ADQUISICIÓN VIVIENDA 1' y 'GRUPO ADQUISICIÓN VIVIENDA 2'\n"
                        "  Dentro de cada grupo suelen aparecer cadenas como:\n"
                        "  'PRIMEROS 12M: 2,15% RESTO: Eur + 0,85% / 1,85%'\n\n"
                        "Reglas de extracción:\n"
                        "1) codigo_administrativo = '<PROD><SUBP>' (concatenar sin guion y sin espacios).\n"
                        "2) codigo_comercial = valor exacto de 'PROD. COM'.\n"
                        "3) Para cada producto que aparezca en el PDF, devuelve un objeto con la forma:\n"
                        "  {\n"
                        '    "codigo_comercial": "<PROD_COM>",\n'
                        '    "codigo_administrativo": "<PROD><SUBP>",\n'
                        '    "tipos_interes_personalizados": {\n'
                        '      "grupo_adquisicion_vivienda_1": "PRIMEROS 12M: ... RESTO: ...",\n'
                        '      "grupo_adquisicion_vivienda_2": "PRIMEROS 12M: ... RESTO: ..."\n'
                        "    }\n"
                        "  }\n"
                        """4) Si algún grupo no aparece explícitamente en el PDF, deja su valor como 
                        cadena vacía ("")."""
                        """5) Conserva el formato de porcentajes y separadores tal como estén en el PDF 
                        (comas decimales, espacios, signos '+'). No inventes valores.\n"""
                        """6) Si el PDF contiene varios productos, devuélvelos todos en el mismo JSON, combinando las 
                    entradas por clave.\n\n"""
                        """**IMPORTANTE**:
                    Añade a la salida calculando las dos siguientes hipotecas con los tipos de interés para ambas 
                    hipotecas según la regla indicada:
                    - Codigos para 'Hipoteca tipo fijo Joven': 
                            codigo_comercial: 112160,
                            codigo_administrativo: 50478
                    - Codigos para 'Hipoteca Joven tipo variable':
                            codigo_comercial: 11200
                            codigo_administrativo: 50476
                        REGLA INDICADA: En las hipotecas 'Joven' se aplica una reducción de 5 puntos (0.05%) en el 
                        diferencial respecto a la hipoteca fidelidad.
                        Realiza este calculo para cada grupo de adquisión y según el tipo de interés (fijo o variable)
                    """
                        f"Contenido del PDF:\n{contenido_pdf}"
                    ),
                },
            ],
            response_model=List[ProductoTiposInteres],
        )

        # Convertir el objeto a diccionario
        array_tipos_interes = [p.model_dump() for p in respuesta]

        return array_tipos_interes

    def procesar(self, pdf_path, cliente, array_tipos_interes: List):

        contenido_pdf = leer_pdf(pdf_path)

        # Llamada al modelo de AI Core
        logger.info("Creando conexión con el modelo de AI Core.")
        respuesta = cliente.chat.completions.create(
            model=ENGINE_ID,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Eres un experto en extraer información estructurada de fichas de productos bancarios. "
                        "Devuelve los campos requeridos como un objeto JSON con subcampos estructurados."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        "Extrae del siguiente documento PDF la siguiente estructura como JSON:"
                        "- nombre_producto"
                        "- codigo_producto { comercial, administrativo }"
                        "- descripcion_producto"
                        "- publico_objetivo"
                        """- condiciones_financieras { destino, importe, plazo, LTV, carencia_de_capital, garantia,
                        amortizacion, moneda, referencia }"""
                        """- tarifas {tipo_de_interes_fijo_con_bonificacion_por_vinculacion, tipos_interes {…},
                          comisiones {…} }"""
                        """- bloques_de_bonificacion_por_mantenimiento_y_contratacion_de_productos
                        [ { producto, bonificacion } ]"""
                        "- bonificacion_maxima"
                        "- periodicidad_de_revision"
                        "- atribuciones_en_condiciones_financieras"
                        "- atribuciones_en_concesion_de_operaciones"
                        "- consideraciones_generales"
                        "- argumentario_comercial"
                        f"Contenido del PDF: {contenido_pdf}"
                    ),
                },
            ],
            response_model=FichaProducto,
        )

        # Convertir el objeto a diccionario
        producto = respuesta.model_dump()

        # Añadir el tipo de interes a la ficha procesada
        item = next(
            (
                p
                for p in array_tipos_interes
                if p["codigo_administrativo"]
                == producto["codigo_producto"]["administrativo"]
            ),
            None,
        )

        # Para obtener solo los tipos de interés:
        tipos_interes = item["tipos_interes_personalizados"] if item else None
        producto["tarifas"]["tipos_interes"] = tipos_interes

        # Usar el código administrativo como clave externa
        ficha_procesada = json.dumps(producto, indent=2, ensure_ascii=False)

        # --- MOVER EL ARCHIVO ---
        fecha = datetime.now()
        year = fecha.year
        month = fecha.month
        day = fecha.day

        ruta_archivo = Path(pdf_path)
        historico_dir = (
            ruta_archivo.parent
            / "HISTORICO"
            / str(year)
            / f"{month:02d}"
            / f"{day:02d}"
        )
        historico_dir.mkdir(
            parents=True, exist_ok=True
        )  # Crea las carpetas si no existen
        destino = historico_dir / ruta_archivo.name
        shutil.move(str(ruta_archivo), str(destino))  # Mueve el archivo
        return ficha_procesada

    def guardar_ficha_producto(self, data: dict) -> None:
        """
        Guarda el contenido JSON de una ficha de producto hipotecario.
        """
        try:
            # Sacamos el codigo administrativo
            data_dict = json.loads(data)
            cod_admin = data_dict["codigo_producto"]["administrativo"]
            ficha_json = json.dumps(data_dict, ensure_ascii=False, indent=2)

            # Crear la entidad
            entidad = FichaProductoHipoteca(
                COD_ID_PROD_HIPO=int(cod_admin), DES_JSON=ficha_json
            )
            self.db_session.merge(entidad)
            self.db_session.commit()

        except SQLAlchemyError as exc:
            self.db_session.rollback()
            raise RepositoryException(f"Error al guardar ficha producto: {exc}")


class LecturaFichaCampanyaService:
    """
    Clase para leer las fichas de las campanias
    """

    _instance = None

    def __init__(self, headers, db_session):
        """
        Inicializa el DAO con una sesión de base de datos ya creada.

        Args:
            db_session: Instancia de sesión de SQLAlchemy para usar.
        """
        self.db_session = db_session
        self.headers = headers

    def procesar(self, cliente):

        ruta_excel = r"\\Gk-ftp01\gw859801\IAG\DESARROLLO\Planificacion 1S25 Estrategia Comercial - Promociones -nuevo formato-.xlsx"

        # Leer sin cabecera
        df_raw = pd.read_excel(ruta_excel, header=None)

        # Asignar nombres de columnas manualmente (saltamos las primeras 9 filas)
        columnas = [
            "Ignorar0",  # col 0
            "Ignorar1",  # col 1
            "Aplicacion",  # col 2  ← aquí está "Particulares"
            "Ignorar3",  # col 3
            "Promocion",  # col 4
            "Descripcion",  # col 5
            "Ene",
            "Feb",
            "Mar",
            "Abr",
            "May",
            "Jun",
            "Jul",
            "Ago",
            "Sept",
            "Oct",
            "Nov",
            "Dic",
        ]

        df = df_raw.iloc[9:].copy()
        df.columns = columnas

        # Rellenar valores vacíos en 'Aplicacion' y en 'Promocion' con el valor anterior
        df["Aplicacion"] = df["Aplicacion"].ffill()
        # Rellenar valores vacíos en 'Aplicacion' con el valor anterior
        df["Promocion"] = df["Promocion"].ffill()

        # Filtrar solo las filas donde Aplicacion es 'particulares' (ignorando mayúsculas y espacios)
        df_particulares = df[
            df["Aplicacion"].astype(str).str.strip().str.lower() == "particulares"
        ]

        meses = [
            "Ene",
            "Feb",
            "Mar",
            "Abr",
            "May",
            "Jun",
            "Jul",
            "Ago",
            "Sept",
            "Oct",
            "Nov",
            "Dic",
        ]

        # Convertir a 1 si hay contenido (no NaN ni vacío), 0 si está vacío o NaN
        df_particulares[meses] = df_particulares[meses].notna().astype(int)
        df_particulares["Promocion"] = (
            df_particulares["Promocion"].str.replace("\n", " ", regex=False).str.strip()
        )
        df_particulares["Descripcion"] = (
            df_particulares["Descripcion"]
            .str.replace("\n", " ", regex=False)  # Saltos de línea por espacio
            .str.replace("•", "-", regex=False)  # Viñetas a guion
            .str.lstrip("-")  # Quitar guion al inicio si existe
            .str.strip()  # Quitar espacios sobrantes
        )

        # Construir texto para enviar al modelo
        texto_para_modelo = ""
        for _, row in df_particulares.iterrows():
            meses_activos = [mes for mes in meses if row[mes] == 1]
            texto_para_modelo += (
                f"Promoción: {row['Promocion']}\n"
                f"Descripción: {row['Descripcion']}\n"
                f"Meses activos: {', '.join(meses_activos)}\n\n"
            )

        # Llamada al modelo OpenAI (adaptada a tu cliente)
        respuesta = cliente.chat.completions.create(
            model=ENGINE_ID,
            messages=[
                {
                    "role": "system",
                    "content": (
                        """
                        Eres un experto en marketing bancario. Extrae campañas promocionales exclusivamente dirigidas a
                        clientes particulares. Ignora cualquier promoción que sea para empresas, autónomos o referida a
                        tarjetas de débito o seguros de decesos.\n\n
                        Incluye solo campañas que estén relacionadas con alguno de los siguientes conceptos clave
                        (ya sea en el título o en la descripción):\n"
                        - Vida\n
                        - Auto\n
                        - Protección pagos\n
                        - Tarjeta crédito\n
                        - Salud\n
                        - Captación haberes\n
                        - Fondos Inversión\n
                        - Planes Pensiones\n
                        - Plan Uniseguro\n\n
                        Devuelve una lista de objetos JSON con los siguientes campos, usando el texto exacto y completo de
                        la descripción, sin resumir:\n
                        - promocion: nombre de la campaña\n
                        - descripcion: texto exacto y completo de la descripción\n
                        - meses_activos: lista de meses en los que la promoción está activa (por ejemplo: ['enero', 'marzo']).
                        """
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        "El documento contiene una tabla con campañas promocionales y columnas correspondientes a los meses del año. "
                        "Interpreta los meses activos para cada promoción según los meses indicados.\n\n"
                        f"{texto_para_modelo}"
                    ),
                },
            ],
            response_model=List[FichaCampania],
        )

        # Convertir a lista de diccionarios
        campanas = [campana.model_dump() for campana in respuesta]
        ficha_campanyas_procesada = json.dumps(campanas, indent=2, ensure_ascii=False)

        return ficha_campanyas_procesada

    def guardar_ficha_campanya(self, ficha_json: str) -> None:
        """
        Guarda el contenido JSON de una ficha de producto hipotecario.
        """
        try:
            entidad = FichaCampanyasHipotecas(DES_JSON=ficha_json)
            self.db_session.add(entidad)
            self.db_session.commit()
        except SQLAlchemyError as exc:
            self.db_session.rollback()
            raise RepositoryException(f"Error al guardar ficha producto: {exc}")


class LecturaTraduccionesService:
    """
    Clase para leer ficheros Excel de traducciones y almacenarlos en base de datos.
    """

    def __init__(self, ruta_directorio: str, db_session):
        self.ruta_directorio = Path(ruta_directorio)
        self.db_session = db_session

    @staticmethod
    def detectar_fecha(texto):
        """Detecta si el texto tiene formato AAAA-MM-DD"""
        import re
        import pandas as pd

        if pd.isna(texto):
            return False
        return bool(re.match(r"^\d{4}-\d{2}-\d{2}$", str(texto)))

    def leer_csv(self, file):
        try:
            df = pd.read_csv(file, sep="|", header=None, dtype=str, encoding="utf-8")
        except UnicodeDecodeError:
            df = pd.read_csv(file, sep="|", header=None, dtype=str, encoding="latin1")

        # Eliminar fechas de extremos
        if df.shape[1] > 0 and self.detectar_fecha(df.iloc[0, 0]):
            df = df.iloc[:, 1:]
        if df.shape[1] > 0 and self.detectar_fecha(df.iloc[0, -1]):
            df = df.iloc[:, :-1]
        return df

    def procesar_dataframe(self, df, file):
        num_cols = df.shape[1]

        # Filtro específico para IAG_DIM_SUBPRODUCTO_
        if file.name.startswith("IAG_DIM_SUBPRODUCTO"):
            df = df[df.iloc[:, 0] == "050"]

        # CNAE con 3 columnas
        if file.name.startswith("IAG_DIM_CNAE") and num_cols == 3:
            df.columns = ["CODIGO", "ABREVIATURA", "NOMBRE"]
            return [
                {
                    row["CODIGO"]: {
                        "ABREVIATURA": row["ABREVIATURA"],
                        "NOMBRE": row["NOMBRE"],
                    }
                }
                for _, row in df.iterrows()
            ]

        # Dos columnas
        if num_cols == 2:
            df = df.dropna(how="all")
            df.columns = ["CLAVE", "VALOR"]
            return [{k: v} for k, v in zip(df["CLAVE"], df["VALOR"])]

        # Cualquier otro CSV
        return df.fillna("").to_dict(orient="records")

    def procesar_fichas(self) -> pd.DataFrame:
        registros = []
        fecha = datetime.now()
        year, month, day = fecha.year, fecha.month, fecha.day

        for file in self.ruta_directorio.glob("*.csv"):
            if file.name.startswith("IAG_MVP_SEGURO_"):
                continue

            try:
                df = self.leer_csv(file)
                data = self.procesar_dataframe(df, file)
                excel_json = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
                tipo_dato = re.sub(r"_\d{8}$", "", file.stem)

                registros.append(
                    {
                        "DES_NOMBRE_FICHERO": file.name,
                        "DES_TIPO_DATO": tipo_dato,
                        "DES_COMPLETA": excel_json,
                    }
                )

                # Mover a histórico
                historico_dir = (
                    self.ruta_directorio
                    / "HISTORICO"
                    / str(year)
                    / f"{month:02d}"
                    / f"{day:02d}"
                )
                historico_dir.mkdir(parents=True, exist_ok=True)
                shutil.move(str(file), str(historico_dir / file.name))

            except Exception as e:
                raise RuntimeError(f"Error leyendo {file.name}: {e}")

        return pd.DataFrame(registros)

    def guardar_traducciones(self, df_traducciones: pd.DataFrame) -> None:
        """
        Inserta o actualiza cada traducción en la tabla MST_TRADUCCIONES usando DES_TIPO_DATO como clave primaria.
        """
        try:
            for row in df_traducciones.itertuples(index=False):
                entidad = FichaTraducciones(
                    DES_TIPO_DATO=row.DES_TIPO_DATO,
                    DES_NOMBRE_FICHERO=row.DES_NOMBRE_FICHERO,
                    DES_COMPLETA=row.DES_COMPLETA,
                    AUD_TIM=datetime.now(),
                )
                self.db_session.merge(entidad)

            self.db_session.commit()
        except SQLAlchemyError as exc:
            self.db_session.rollback()
            raise RepositoryException(f"Error al guardar traducciones: {exc}")
