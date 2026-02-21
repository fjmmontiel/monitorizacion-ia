"""Modulo para test"""

import pytest
from unittest.mock import patch
from app.tools.tools_muestra_interes import calcular_tiempo_transcurrido


def test_calcular_tiempo_transcurrido():
    """Modulo para test"""

    # Simula dos fechas con diferencia de 3600 segundos (1 hora)
    from datetime import datetime, timedelta

    inicio = datetime(2024, 1, 1, 12, 0, 0)
    ahora = inicio + timedelta(seconds=3600)

    with patch(
        "app.tools.tools_muestra_interes.parsear_fecha", side_effect=[inicio, ahora]
    ), patch(
        "app.tools.tools_muestra_interes.obtener_hora_actual",
        return_value="2024-01-01 13:00:00",
    ):
        resultado = calcular_tiempo_transcurrido("2024-01-01 12:00:00")
        assert resultado == 3600.0
