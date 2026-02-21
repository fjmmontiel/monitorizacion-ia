"""
Tests para Session.
Valida la gestión de sesiones y el cálculo de costes y tiempos.
"""

import pytest
from datetime import datetime, timedelta
from app.managers.session_manager import Session


def test_session_creation_and_attributes():
    """Testea la creación de una sesión y sus atributos básicos."""
    session = Session("test_id", "8888", "UX9999A")
    assert session.session_id == "test_id"
    assert session.input_tokens == 0
    assert session.output_tokens == 0
    assert session.cost == 0.0
    assert session.valoracion == -1
    assert session.comentarios == ""
    assert session.session_duration == 0
    assert session.session_start is None
    assert session.session_end is None


def test_session_calcular_costes_dolares():
    """Testea el cálculo de costes en dólares."""
    session = Session("test_id", "8888", "UX9999A")
    session.input_tokens = 1000000
    session.output_tokens = 2000000
    coste = session.calcular_costes_dolares()
    assert pytest.approx(coste, 0.01) == 22.5
    assert session.cost == coste


def test_session_iniciar_y_actualizar_tiempos():
    """Testea el inicio y actualización de tiempos de sesión."""
    session = Session("test_id", "8888", "UX9999A")
    session.iniciar_sesion()
    assert isinstance(session.session_start, datetime)
    # Simula que la sesión dura 10 segundos
    session.session_start -= timedelta(seconds=10)
    session.actualizar_tiempos_sesion()
    assert session.session_end is not None
    assert 9 <= session.session_duration <= 11  # margen de error
