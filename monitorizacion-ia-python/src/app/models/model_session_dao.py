"""
Modelo de datos para métricas de sesión.

Define la estructura de la tabla MST_SESION para almacenar
métricas y metadatos de sesiones de usuario, con conversión
entre modelo SQLAlchemy y objetos Session.
"""

from sqlalchemy import (
    Column,
    Integer,
    Numeric,
)
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER, NVARCHAR, DATETIME2
from sqlalchemy.ext.declarative import declarative_base
from app.managers.session_manager import Session
from typing import List, Optional
from pydantic import BaseModel


Base = declarative_base()


class FilterOptions(BaseModel):
    """
    Representa un filtro individual para la búsqueda de sesiones.

    Atributos:
        campo (str): Nombre del campo en la base de datos o modelo sobre el que se aplica el filtro.
        valor (str): Valor que se utilizará para filtrar el campo especificado.
    """

    campo: str
    valor: str


class SesionSortAndFilterOptions(BaseModel):
    """
    Define las opciones de paginación, ordenación y filtrado para la búsqueda de sesiones.

    Atributos:
        pagina (Optional[int]): Número de página para la paginación (1-indexed). Puede ser None si no se especifica.
        tamano (Optional[int]): Cantidad de registros por página. Puede ser None si no se especifica.
        campoOrden (Optional[str]): Campo por el que se ordenarán los resultados. Puede ser None si no se especifica.
        direccionOrden (Optional[str]): Dirección de la ordenación ('asc' o 'desc'). Puede ser None si no se especifica.
        filtros (List[FilterOptions]): Lista de filtros aplicados a la búsqueda.
        Cada filtro contiene un campo y un valor.
    """

    pagina: Optional[int] = None
    tamano: Optional[int] = None
    campoOrden: Optional[str] = None
    direccionOrden: Optional[str] = None
    filtros: List[FilterOptions] = []


class SessionModel(Base):
    """
    Clase para manejar el modelo de los datos que se guardan pertenecientes a la sesion
    """

    __tablename__ = "MST_SESION"

    COD_ID_SESION_UNIQUE = Column(
        UNIQUEIDENTIFIER, primary_key=True, unique=True, nullable=False
    )
    NUM_INPUT_TOKENS = Column(Integer, nullable=True)
    NUM_OUTPUT_TOKENS = Column(Integer, nullable=True)
    POC_COSTE = Column(Numeric(18, 8), nullable=True)
    NUM_VALORACION = Column(Integer, nullable=True)
    DES_COMENTARIOS = Column(NVARCHAR(100), nullable=True)
    NUM_MUESTRA_INTERES = Column(Integer, nullable=True)
    NUM_SESION_DURACION = Column(Integer, nullable=True)
    AUD_TIM_SESION_INI = Column(DATETIME2, nullable=True)
    AUD_TIM_SESION_FIN = Column(DATETIME2, nullable=True)
    COD_CENTRO_SESION = Column(NVARCHAR(4), nullable=True)
    COD_GESTOR_SESION = Column(NVARCHAR(8), nullable=True)
    DES_CONVERSACION = Column(NVARCHAR, nullable=True)

    def to_session(self):
        """Convierte el modelo de SQLAlchemy a un objeto Session"""
        session = Session(
            self.COD_ID_SESION_UNIQUE, self.COD_CENTRO_SESION, self.COD_GESTOR_SESION
        )
        session.input_tokens = self.NUM_INPUT_TOKENS
        session.output_tokens = self.NUM_OUTPUT_TOKENS
        session.cost = float(self.POC_COSTE)
        session.valoracion = self.NUM_VALORACION
        session.comentarios = self.DES_COMENTARIOS
        session.muestra_de_interes = self.NUM_MUESTRA_INTERES
        session.session_duration = self.NUM_SESION_DURACION
        session.session_start = self.AUD_TIM_SESION_INI
        session.session_end = self.AUD_TIM_SESION_FIN
        session.conversacion = self.DES_CONVERSACION
        # El campo ultima_llamada_guardar_muestra_de_interes no está en la base de datos
        # pero existe en el modelo Session
        session.ultima_llamada_guardar_muestra_de_interes = ""
        return session
