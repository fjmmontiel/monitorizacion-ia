"""
Módulo que define la clase `DataSession` para interactuar con datos relacionados con productos hipotecarios,
traducciones y campañas en la base de datos SQL Server. Proporciona métodos para listar productos, obtener
traducciones y recuperar campañas activas según el mes actual.

Clases:
    DataSession: Implementa la lógica de acceso y consulta a datos de fichas y campañas.

"""

from sqlalchemy import select, desc
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
import json

from app.models.models_fichas import (
    FichaProductoHipoteca,
    FichaTraducciones,
    FichaCampanyasHipotecas,
)

from app.repositories.sqlserver.database_connector import get_manual_db_session


class DataSession:
    """Modulo"""

    def __init__(self):
        """
        Clase para la interaccion con datos en la base de datos.
        """
        # init vacío intencionalmente, no se reuqiere logia al crear la instancia
        pass

    def listar_productos(self, codigo_administrativo: str = None):
        """
        Devuelve todos los registros de productos hipotecarios, opcionalmente filtrando por código administrativo.

        Args:
            codigo_administrativo (str, opcional): Código administrativo del producto.
                                                Si se proporciona, solo devuelve ese producto.

        Returns:
            List[FichaProductoHipoteca]: Lista de productos hipotecarios.
        """
        try:
            db_session = get_manual_db_session()
            query = select(FichaProductoHipoteca)
            if codigo_administrativo:
                query = query.where(
                    FichaProductoHipoteca.COD_ID_PROD_HIPO == codigo_administrativo
                )

            return db_session.execute(query).scalars().all()
        except SQLAlchemyError as e:
            raise RuntimeError(f"Error al listar productos en base de datos: {e}")
        finally:
            db_session.close()

    def get_traduccion(
        self,
        tipo_dato: str,
    ):
        """
        Recupera las traducciones para un tipo de datos
        """
        try:
            db_session = get_manual_db_session()

            # Buscar la fila que coincida con DES_TIPO_DATO
            registro = (
                db_session.query(FichaTraducciones)
                .filter_by(DES_TIPO_DATO=tipo_dato)
                .first()
            )
            if registro is None:
                return {"error": "No se ha encontrado DEST_TIPO_DATO = {tipo_dato}"}

            data = json.loads(registro.DES_COMPLETA)
            db_session.close()
            return data

        except Exception as e:
            return {
                "error": f"No se pudo obtener las traducciones para {tipo_dato}: {e}"
            }
        finally:
            db_session.close()

    def get_campanyas(
        self,
    ):
        """
        Recupera las traducciones para un tipo de datos
        """
        try:
            db_session = get_manual_db_session()
            mes_actual_index = datetime.now().month
            meses_es = [
                "enero",
                "febrero",
                "marzo",
                "abril",
                "mayo",
                "junio",
                "julio",
                "agosto",
                "septiembre",
                "octubre",
                "noviembre",
                "diciembre",
            ]
            mes_actual = meses_es[mes_actual_index - 1]

            result = (
                db_session.query(FichaCampanyasHipotecas.DES_JSON)
                .order_by(desc(FichaCampanyasHipotecas.FEC_ALTA_CAMPANIA))
                .first()
            )

            result = db_session.query(FichaCampanyasHipotecas.DES_JSON).first()
            if result is None:
                return {"error": "No se han encontrado campañas en base de datos"}
            des_json = result.DES_JSON
            campanyas_array = json.loads(des_json)
            campanyas_activas = [
                c
                for c in campanyas_array
                if mes_actual in [m.lower() for m in c["meses_activos"]]
            ]

            return campanyas_activas

        except Exception as e:
            return {"error": f"No se pudo obtener las campañas: {e}"}
        finally:
            db_session.close()
