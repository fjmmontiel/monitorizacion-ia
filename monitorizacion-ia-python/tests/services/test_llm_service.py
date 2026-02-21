"""Modulo para test"""

import pytest
from datetime import datetime
import uuid
from app.services.llm_service import (
    generar_identificador_sesion,
)

from app.tools.tools_muestra_interes import obtener_hora_actual, parsear_fecha

from qgdiag_lib_arquitectura.exceptions.types import InternalServerErrorException

from unittest.mock import AsyncMock, patch


# ------------------------------
# Test generar_identificador_sesion
# ------------------------------
def test_generar_identificador_sesion():
    """Modulo para test"""

    identificador = generar_identificador_sesion()
    # Debe ser un string
    assert isinstance(identificador, str)
    # Debe ser un UUID válido
    uuid_obj = uuid.UUID(identificador)
    assert str(uuid_obj) == identificador


# ------------------------------
# Test obtener_hora_actual
# ------------------------------
def test_obtener_hora_actual():
    """Modulo para test"""

    hora = obtener_hora_actual()
    assert isinstance(hora, str)
    # Formato correcto YYYY-MM-DD HH:MM:SS
    datetime.strptime(hora, "%Y-%m-%d %H:%M:%S")


# ------------------------------
# Test parsear_fecha
# ------------------------------
def test_parsear_fecha_valida():
    """Modulo para test"""

    fecha_str = "2025-09-01 12:30:45"
    fecha_obj = parsear_fecha(fecha_str)
    assert isinstance(fecha_obj, datetime)
    assert fecha_obj.year == 2025
    assert fecha_obj.month == 9


def test_parsear_fecha_invalida():
    """Modulo para test"""

    fecha_str = "invalid date"
    fecha_obj = parsear_fecha(fecha_str)
    assert isinstance(fecha_obj, datetime)


from app.services.llm_service import sumar_numeros


def test_sumar_numeros_basico():
    """Modulo para test"""

    datos = {"a": 10, "b": 5.5, "c": "no", "d": None}
    resultado = sumar_numeros(datos)
    assert resultado == 15.5


def test_sumar_numeros_vacio():
    """Modulo para test"""

    datos = {}
    resultado = sumar_numeros(datos)
    assert resultado == 0


def test_sumar_numeros_solo_no_numericos():
    """Modulo para test"""

    datos = {"x": "a", "y": None, "z": []}
    resultado = sumar_numeros(datos)
    assert resultado == 0


def test_sumar_numeros_negativos():
    """Modulo para test"""

    datos = {"a": -10, "b": 5, "c": -2.5}
    resultado = sumar_numeros(datos)
    assert resultado == -7.5
