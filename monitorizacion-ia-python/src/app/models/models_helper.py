"""
Utilidades de ayuda para modelos de datos.

Proporciona funciones auxiliares para consultar traducciones
y otros datos relacionados con modelos desde la base de datos.
"""

from app.repositories.sqlserver.session_data_dao import DataSession


def get_traduccion_from_db(tipo_dato: str):
    """
    Obtiene traducciones de códigos desde la base de datos.

    Args:
        tipo_dato: Tipo de dato para el cual obtener la traducción

    Returns:
        dict: Diccionario con la traducción o mensaje de error
    """

    try:
        # Creamos sesión de base de datos
        db_session = DataSession()

        # Usamos el método listar_productos con filtro por código administrativo
        traduccion = db_session.get_traduccion(tipo_dato=tipo_dato)

        return {
            "Traducción de códigos para {tipo_dato}": traduccion,
        }

    except Exception as e:
        return {
            "error": f"Error al consultar la traduccion de de datos: {str(e)}",
        }
