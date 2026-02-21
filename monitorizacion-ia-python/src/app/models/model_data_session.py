"""
Modelo de datos para persistencia de sesiones.

Define la estructura de la tabla MST_DATOS_SESION para almacenar
información de contexto y datos de sesión en SQL Server.
"""


from sqlalchemy import Column, Integer
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER, NVARCHAR, BIT, DATETIME2
from sqlalchemy.orm import declarative_base
import uuid

Base = declarative_base()


class DatosSesionTable(Base):
    """
    Modelo SQLAlchemy para la tabla MST_DATOS_SESION.
    
    Almacena datos de contexto de sesiones con información JSON,
    timestamps de auditoría y validación de datos.
    """


    __tablename__ = "MST_DATOS_SESION"

    COD_ID_SESION = Column(Integer, primary_key=True, autoincrement=True)
    COD_ID_SESION_UNIQUE = Column(
        UNIQUEIDENTIFIER,
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        unique=True,
    )
    COD_ID_DATO_UNIQUE = Column(NVARCHAR(100), nullable=False)
    DES_TIPO_DATO = Column(NVARCHAR(100), nullable=False)
    DES_JSON = Column(NVARCHAR(None), nullable=False)
    AUD_TIM = Column(DATETIME2, nullable=False)
    IND_DATO_VALIDO = Column(BIT, nullable=False)
