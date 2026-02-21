""" Modulo para test """

import pytest
from app.services.llm_service import calcular_cuota_mensual

def test_calcular_cuota_mensual_ok():
    """ Modulo para test """

    capital = 100000
    interes_anual = 2.5
    num_cuotas = 12
    dias_por_mes = [30] * 12  # 12 meses de 30 días
    cuota = calcular_cuota_mensual(capital, interes_anual, num_cuotas, dias_por_mes)
    assert isinstance(cuota, float)
    assert cuota > 0

def test_calcular_cuota_mensual_error():
    """ Modulo para test """

    capital = 100000
    interes_anual = 2.5
    num_cuotas = 12
    dias_por_mes = [30] * 10  # Incorrecto: solo 10 meses
    with pytest.raises(ValueError) as excinfo:
        calcular_cuota_mensual(capital, interes_anual, num_cuotas, dias_por_mes)
    assert "debe tener el mismo" in str(excinfo.value)
