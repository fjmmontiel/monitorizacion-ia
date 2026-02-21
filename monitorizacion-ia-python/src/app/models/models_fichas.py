"""
Modelos para fichas de productos hipotecarios y bonificaciones.

Define modelos SQLAlchemy y Pydantic para gestionar información de productos,
campañas, bonificaciones y traducciones del sistema de hipotecas.
"""

from pydantic import BaseModel  # type: ignore
from typing import List, Dict, Optional, Union
from pydantic import BaseModel, Field
from datetime import datetime


from sqlalchemy import Column, Integer, Numeric, DateTime, UnicodeText, NVARCHAR
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class FichaBonificaciones(Base):
    """
    Clase para definir el modelos de datos de FichaBonificaciones
    """

    __tablename__ = "MST_BONIFICACION"

    COD_ADMINISTRATIVO = Column(Integer, primary_key=True)
    DES_CONCEPTO = Column(NVARCHAR(None), primary_key=True)
    COD_ID_BLOQUE = Column(Integer, primary_key=True)
    PCT_BONIFICACION_MAX = Column(Numeric(5, 2), nullable=False)
    PCT_BONIFICACION = Column(Numeric(5, 2), nullable=False)
    DES_COMPLETA = Column(NVARCHAR(None))


class FichaProductoHipoteca(Base):
    """
    Clase para definir el modelos de datos de FichaProductoHipoteca
    """

    __tablename__ = "MST_PRODUCTO_HIPOTECAS"

    COD_ID_PROD_HIPO = Column(Integer, primary_key=True, nullable=False)
    DES_JSON = Column(NVARCHAR(None), nullable=False)
    AUD_TIM = Column(DateTime, default=datetime.now, nullable=False)


class FichaCampanyasHipotecas(Base):
    """
    Clase para definir el modelos de datos de FichaCampanyasHipotecas
    """

    __tablename__ = "MST_CAMPANIA_HIPOTECAS"

    COD_ID_CAMPANIA = Column(Integer, primary_key=True, autoincrement=True)
    FEC_ALTA_CAMPANIA = Column(DateTime(timezone=False), default=func.sysdatetime())
    DES_JSON = Column(UnicodeText, nullable=False)


class FichaTraducciones(Base):
    """
    Clase para definir el modelos de datos de FichaTraducciones
    """

    __tablename__ = "MST_TRADUCCIONES"

    DES_NOMBRE_FICHERO = Column(NVARCHAR(255), nullable=False)
    DES_TIPO_DATO = Column(NVARCHAR(255), primary_key=True, nullable=False)
    DES_COMPLETA = Column(NVARCHAR(None), nullable=False)
    AUD_TIM = Column(DateTime, default=datetime.now, nullable=False)


class CodigoProducto(BaseModel):
    """
    Clase para definir el modelos de datos de CodigoProducto
    """

    comercial: str = Field(description="Código comercial del producto")
    administrativo: str = Field(description="Código administrativo del producto")


class CondicionesFinancieras(BaseModel):
    """
    Clase para definir el modelos de datos de CondicionesFinancieras
    """

    destino: Optional[str] = None
    importe: Optional[str] = None
    plazo: Optional[str] = None
    LTV: Optional[str] = None
    carencia_de_capital: Optional[str] = None
    garantia: Optional[str] = None
    amortizacion: Optional[str] = None
    moneda: Optional[str] = None
    referencia: Optional[str] = None


class Tarifas(BaseModel):
    """
    Clase para definir el modelos de datos de Tarifas
    """

    tipo_de_interes_fijo_con_bonificacion_por_vinculacion: str
    tipos_interes: Dict[str, str]
    comisiones: Dict[str, str]


class Bonificacion(BaseModel):
    """
    Clase para el modelo de datos de la Bonificacion
    """

    nombre: Optional[str] = Field(description="Nombre de la bonificación")
    valor: Optional[float] = Field(
        description="""Valor incremental de la bonificación en puntos porcentuales (siempre en positivo)"""
    )


class FichaProducto(BaseModel):
    """
    Clase para definir el modelos de datos de FichaProducto
    """

    nombre_producto: Optional[str] = None
    codigo_producto: Optional[CodigoProducto] = None
    descripcion_producto: Optional[str] = None
    publico_objetivo: Optional[str] = None
    condiciones_financieras: Optional[CondicionesFinancieras] = None
    tarifas: Optional[Tarifas] = None
    bloques_de_bonificacion_por_mantenimiento_y_contratacion_de_productos: Optional[
        List[Bonificacion]
    ] = None
    bonificacion_maxima: Optional[str] = None
    periodicidad_de_revision: Optional[str] = None
    atribuciones_en_condiciones_financieras: Optional[str] = None
    atribuciones_en_concesion_de_operaciones: Optional[str] = None
    consideraciones_generales: Optional[Union[str, dict]] = None
    argumentario_comercial: Optional[Union[str, dict]] = None


# Modelo para estructurar campañas
class FichaCampania(BaseModel):
    """
    Clase para definir el modelos de datos de FichaCampania
    """

    promocion: str = Field(description="Nombre o título de la promoción")
    descripcion: str = Field(description="Breve descripción de la promoción")
    meses_activos: List[str] = Field(
        description="Lista de meses en los que está activa la campaña"
    )


class ParametrosCalculoBonificaciones(BaseModel):
    """
    Clase para el modelo de datos de la ParametrosCalculoBonificaciones
    """

    codigo_administrativo: Optional[str] = Field(
        description="Código administrativo del producto hipotecario sobre el que se realiza el cálculo",
    )
    grupo_adquisicion: Optional[str] = Field(
        description="""Grupo adquisición del que se han obtenido las tarifas. Valores posibles:
        grupo_adquisicion_vivienda_1, grupo_adquisicion_vivienda_2, grupo_no_adquisicion_vivienda""",
    )
    bonificaciones: Optional[List[Bonificacion]] = Field(
        default=None,
        description="Bonificaciones a aplicar para hacer el cálculo",
    )


class TiposInteres(BaseModel):
    grupo_adquisicion_vivienda_1: str = Field(
        ..., description="Ej: 'PRIMEROS 12M: 2,15% RESTO: Eur + 0,85% / 1,85%'"
    )
    grupo_adquisicion_vivienda_2: str = Field(
        ..., description="Ej: 'PRIMEROS 12M: 2,15% RESTO: Eur + 0,60% / 1,60%'"
    )


class ProductoTiposInteres(BaseModel):
    codigo_comercial: str = Field(..., description="Ej: '112003'")
    codigo_administrativo: str = Field(..., description="Ej: '050460' (6 dígitos)")
    tipos_interes_personalizados: TiposInteres
