"""
Modulo para manejar los diferentes endpoints del escalado
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse, JSONResponse
import json
import os
import uuid
from pathlib import Path
from sqlalchemy import and_
from sqlalchemy.orm import Session as SQLAlchemySession
from langchain_core.messages import AIMessage
from datetime import datetime
from app.constants.global_constants import GlobalConstants
import httpx

from app.services.llm_service import LangchainLLMService
from app.services.lectura_fichas_service import (
    LecturaFichaProductoService,
    LecturaFichaCampanyaService,
    LecturaTraduccionesService,
    conexion_modelo,
)
from app.repositories.sqlserver.database_connector import get_db_session
from app.routes.common import get_llm_service
from app.models.models import Messages
from app.models.models_resto import SubirFichero
from app.models.model_data_session import DatosSesionTable
import requests
from fastapi import Request
from app.settings import settings
from app.repositories.sqlserver.session_dao import SessionDAO
from app.models.model_session_dao import SesionSortAndFilterOptions
from app.managers.distributed_context import distributed_session_manager

from qgdiag_lib_arquitectura.security.authentication import (
    get_authenticated_headers,
    get_user_id,
)
from qgdiag_lib_arquitectura import CustomLogger
from qgdiag_lib_arquitectura.exceptions.types import ExceptionTErrorInterno
from typing import Any

router = APIRouter()

logger = CustomLogger("hipotecas_process_service")

URL_TOKEN_JWT = settings.URL_TOKEN_JWT


def validate_authorize_request(request: Request) -> bool:
    """Validación de token y pertenencia a grupo en LDAP"""

    # Bypass total en dev
    if settings.ENVIRONMENT == "development":
        logger.info("Entorno 'dev': autorización forzada (return True).")
        return True

    sub_id = get_user_id(request)
    token = request.headers.get("Token") or request.headers.get("token")

    logger.info(
        f"""Autorizando usuario: {sub_id} en la aplicación: {settings.LDAP_APP} con el token: {token}..."""
    )

    if not sub_id:
        raise HTTPException(
            status_code=401, detail="No autorizado, usuario no especificado en el token"
        )

    if not token:
        raise HTTPException(
            status_code=401, detail="Token no encontrado en la cabecera"
        )
    try:

        headers = {
            "Channel": "iag",
            "Token": token,
        }

        resp = requests.get(
            settings.LDAP_URL,
            headers=headers,
            params={"usuarioId": sub_id, "aplicacionId": settings.LDAP_APP},
            timeout=10,
            verify=True,
        )

        if resp.status_code != 200:
            raise HTTPException(
                status_code=401,
                detail=f"Error al validar el usuario contra LDAP (status {resp.status_code})",
            )

        is_authorized = resp.text.strip().lower() == "true"

        if not is_authorized:
            raise HTTPException(
                status_code=403, detail=f"Usuario {sub_id} no tiene permisos"
            )
        else:
            logger.info("Usuario autorizado!")

    except requests.RequestException as e:
        raise HTTPException(
            status_code=401, detail=f"Error en la llamada a {settings.LDAP_URL}: {e}"
        )
    else:
        print(f"Usuario validado y autorizado: {sub_id}")

        return is_authorized


@router.post("/chat", tags=["Chat"])
async def chat(
    body: Messages,
    background_tasks: BackgroundTasks,
    headers: dict = Depends(get_authenticated_headers),
    llm_service: LangchainLLMService = Depends(get_llm_service),
    autorizado: bool = Depends(validate_authorize_request),
):
    """
    Funcion para ejecutar el chat en streaming con soporte para contexto distribuido
    """
    try:
        headers["IAG-App-Id"] = settings.IAG_APP_ID

        logger.info(f"Headers: {headers}")
        await llm_service.init_async(headers)

        # Obtener o generar session_id
        llm_service.add_messages(body.messages)

        session_id = body.idSesion
        # session_id = llm_service.get_session_id()

        if not session_id:
            session_id = str(uuid.uuid4())
            logger.info(f"Generado nuevo session_id: {session_id}")
        else:
            logger.info(f"Usando session_id proporcionado: {session_id}")

        # Configurar el contexto distribuido para el LLM service

        distributed_context = distributed_session_manager.create_context(
            session_id, headers
        )

        # Configurar el LLM service con el contexto distribuido (siempre requerido)
        llm_service.set_distributed_context(distributed_context)

        # await llm_service.init()
        stream = llm_service.chat(background_tasks, headers)

        async def event_generator():
            """Modulo para generación de eventos"""
            # Enviar el session_id en el primer chunk
            yield f"data: {json.dumps({'session_id': session_id})}\n\n"

            last_message = ""
            async for message in stream:
                last_message += message
                yield f"data: {json.dumps({'chunk': message})}\n\n"

            # añadimos el último mensaje del bot
            llm_service.message_history.append(AIMessage(content=last_message))
            llm_service.distributed_context.session_metrics.conversacion = json.dumps(
                [m.model_dump() for m in llm_service.message_history]
            )

            # guardar session_metrics
            llm_service.save_session()

            yield f"data: {json.dumps({'done':'[DONE]'})}\n\n"

        return StreamingResponse(event_generator(), media_type="text/event-stream")

    except Exception as e:
        logger.exception("Error interno en el endpoint 'chat' durante el streaming")

        raise ExceptionTErrorInterno(
            message=f"Error Interno en el endpoint 'chat': {str(e)}"
        ) from e


@router.get("/get-context-item", tags=["Context"])
async def get_context_item(
    id: str,
    db_session: SQLAlchemySession = Depends(get_db_session),
    headers: dict = Depends(get_authenticated_headers),
):
    """
    Devuelve el item de contexto solicitado (por id) en formato json

    :param id: ID del item solicitado
    :param session_id: ID de la sesión

    :return: Item de contexto en formato json
    :raises HTTPException: Si se produce cualquier tipo de error.
    """
    try:
        item = (
            db_session.query(DatosSesionTable)
            .filter(and_(DatosSesionTable.COD_ID_DATO_UNIQUE == id))
            .all()
        )

        if item:
            resultado = json.loads(item[0].DES_JSON)
        else:
            raise HTTPException(
                status_code=404, detail=f"Objeto con id {id} no encontrado: {str(e)}"
            )

        return resultado

    except Exception as e:
        logger.exception(f"Error cargando el item del contexto {id}: {str(e)}")
        raise ExceptionTErrorInterno(
            message=f"Error cargando el item del contexto {id}: {str(e)}"
        ) from e


@router.post("/procesar/ficha-productos")
async def procesar_ficha_producto(
    db_session: SQLAlchemySession = Depends(get_db_session),
    headers: dict = Depends(get_authenticated_headers),
):
    """
    Endpoint que procesa un PDF con información bancaria y extrae una ficha de producto estructurada.

    Args:
        headers (dict): Cabeceras de la solicitud autenticada, obtenidas mediante `get_authenticated_headers`.

    Returns:
        dict: Resultado del procesamiento con estructura JSON.
    """

    logger.info("Recibida petición para cargar fichas de productos")

    try:

        lectura_ficha_producto = LecturaFichaProductoService(headers, db_session)
        cliente = await conexion_modelo(headers)
        # PROCESAMIENTO DE TIPOS DE INTERES
        ruta_tipos_interes = "https://intranet.unicaja.es/cs/getDocumento/6572"
        array_tipos_interes = lectura_ficha_producto.procesar_tipos_interes(
            pdf_path=ruta_tipos_interes, cliente=cliente
        )

        # PROCESAMIENTO DE FICHAS
        carpeta_path_pdf = r"\\Gk-ftp01\gw859801\IAG\DESARROLLO\PRODUCTOS"
        ruta_path = Path(carpeta_path_pdf)
        for pdf_file in ruta_path.glob("*.pdf"):
            json_ficha_producto = lectura_ficha_producto.procesar(
                pdf_path=pdf_file,
                cliente=cliente,
                array_tipos_interes=array_tipos_interes,
            )
            lectura_ficha_producto.guardar_ficha_producto(json_ficha_producto)
        return {
            "estado": 200,
            "detalle": GlobalConstants.MESSAGE_EXECUTE_ENDPOINT_PROCESS_200_SUCCESS,
            "contenido": [
                {
                    "producto": "Se han almacenado correctamente todos los productos en base de datos."
                }
            ],
        }

    except Exception as e:
        logger.exception("Error interno al procesar fichas de productos")
        raise ExceptionTErrorInterno(
            message=f"Error Interno al procesar fichas de productos: {str(e)}"
        ) from e


@router.post("/procesar/ficha-campanas")
async def procesar_ficha_campana(
    db_session: SQLAlchemySession = Depends(get_db_session),
    headers: dict = Depends(get_authenticated_headers),
):
    """
    Endpoint que procesa un PDF con información bancaria y extrae una ficha de campanyas estructurada.

    Args:
        headers (dict): Cabeceras de la solicitud autenticada, obtenidas mediante `get_authenticated_headers`.

    Returns:
        dict: Resultado del procesamiento con estructura JSON.
    """

    logger.info("Recibida petición para cargar campañas")

    try:
        cliente = await conexion_modelo(headers)
        lectura_ficha_campanya = LecturaFichaCampanyaService(headers, db_session)
        ficha_campanyas_procesada = lectura_ficha_campanya.procesar(cliente=cliente)
        lectura_ficha_campanya.guardar_ficha_campanya(ficha_campanyas_procesada)

        return {
            "estado": 200,
            "detalle": GlobalConstants.MESSAGE_EXECUTE_ENDPOINT_PROCESS_200_SUCCESS,
            "contenido": [{"Campañas": ficha_campanyas_procesada}],
        }
    except Exception as e:
        logger.exception("Error interno en al procesar la ficha de campañas")
        raise ExceptionTErrorInterno(
            message=f"Error Interno al procesar la ficha de campañas: {str(e)}"
        ) from e


@router.post("/procesar/ficha-traducciones")
async def procesar_traducciones(
    db_session: SQLAlchemySession = Depends(get_db_session),
    headers: dict = Depends(get_authenticated_headers),
):
    """
    Procesa los Excels de traducciones y guarda su contenido en MST_TRADUCCIONES.
    """
    logger.info("Recibida petición para cargar traducciones")

    try:
        ruta_prueba = "/mnt/datos"
        ruta_sic = os.path.join(ruta_prueba, "SIC")
        if not os.path.isdir(ruta_sic):
            os.makedirs(ruta_sic, exist_ok=True)

        objetos = os.listdir(ruta_prueba)

        return {
            "estado": 200,
            "detalle": GlobalConstants.MESSAGE_EXECUTE_ENDPOINT_PROCESS_200_SUCCESS,
            "contenido": [{"objetos": objetos}],
        }

        # ruta_directorio = r"\\Gk-ftp01\gw859801\IAG\DESCARGAS_SIC"
        # ruta_directorio = r""
        # servicio_traducciones = LecturaTraduccionesService(ruta_directorio, db_session)

        # df_traducciones = servicio_traducciones.procesar_fichas()
        # servicio_traducciones.guardar_traducciones(df_traducciones)

        # return {
        #     "estado": 200,
        #     "detalle": GlobalConstants.MESSAGE_EXECUTE_ENDPOINT_PROCESS_200_SUCCESS,
        #     "contenido": df_traducciones.to_dict(orient="records"),
        # }
    except Exception as e:
        logger.exception("Error interno en al procesar traducciones")

        raise ExceptionTErrorInterno(
            message=f"Error Interno al procesar traducciones: {str(e)}"
        ) from e


@router.post("/sesiones", tags=["Monitorización"])
async def get_sesion_list(
    options: SesionSortAndFilterOptions,
):
    """
    Obtiene el listado de sesiones

    :return: Listado completo de sesiones en formato JSON
    """
    try:
        session_dao = SessionDAO()
        sesiones = session_dao.get_sessions(options)

        if not sesiones:
            return JSONResponse(content=[], status_code=200)

        # Convertir a dict y eliminar 'conversacion'
        sesiones_dict = []
        for s in sesiones:
            data = s.__dict__
            data.pop("conversacion", None)  # elimina si existe

            # UUID -> str
            if isinstance(data.get("session_id"), uuid.UUID):
                data["session_id"] = str(data["session_id"])

            # datetime -> str (ISO 8601)
            for campo in ("session_start", "session_end"):
                if isinstance(data.get(campo), datetime):
                    data[campo] = data[
                        campo
                    ].isoformat()  # e.g., '2025-12-09T17:35:12.123456'

            sesiones_dict.append(data)

        return JSONResponse(content=sesiones_dict, status_code=200)

    except Exception as e:
        logger.exception("Error cargando el listado de sesiones")

        raise ExceptionTErrorInterno(
            message=f"Error cargando el listado de sesiones: {str(e)}"
        ) from e


@router.get("/conversacion/{id}", tags=["Monitorización"])
async def get_conversacion(
    id: str,
    headers: dict = Depends(get_authenticated_headers),
) -> Any:
    """
    Devuelve la conversación asociada al `id` indicado.

    """
    try:

        return {
            "estado": 200,
            "detalle": GlobalConstants.MESSAGE_EXECUTE_ENDPOINT_PROCESS_200_SUCCESS,
            "contenido": "TO DO",
        }
    except Exception as e:
        logger.exception(f"Error en /conversacion/{id}: {str(e)}")
        raise ExceptionTErrorInterno(
            message=f"Error al procesar la conversación {id}: {str(e)}"
        ) from e


@router.get("/contextoSesion/{id}", tags=["Monitorización"])
async def get_contexto_sesion(
    id: str,
    headers: dict = Depends(get_authenticated_headers),
) -> Any:
    """
    Devuelve el contexto de sesión asociado al `id` indicado.

    """
    try:
        return {
            "estado": 200,
            "detalle": GlobalConstants.MESSAGE_EXECUTE_ENDPOINT_PROCESS_200_SUCCESS,
            "contenido": "TO DO",
        }
    except Exception as e:
        logger.exception(f"Error en /contextoSesion/{id}: {str(e)}")
        raise ExceptionTErrorInterno(
            message=f"Error al procesar el contexto de sesión {id}: {str(e)}"
        ) from e


@router.post("/subirFichero", tags=["Subir fichero"])
async def subir_fichero(
    data: SubirFichero,
    headers: dict = Depends(get_authenticated_headers),
) -> Any:
    """
    Devuelve el contexto de sesión asociado al `id` indicado.

    """
    try:
        return {
            "estado": 200,
            "detalle": GlobalConstants.MESSAGE_EXECUTE_ENDPOINT_PROCESS_200_SUCCESS,
            "contenido": "TO DO",
        }
    except Exception as e:
        logger.exception(f"Error en /subirFichero: {str(e)}")
        raise ExceptionTErrorInterno(
            message=f"Error al procesar la subida del fichero: {str(e)}"
        ) from e
