"""Tests para calcular_cuota_hipoteca."""

import pytest
from unittest.mock import patch
from app.services.llm_service import calcular_cuota_hipoteca


async def _call_tool(payload: dict):
    """
    Invoca la tool de forma compatible con distintas versiones de LangChain:
    - Preferente: .ainvoke(payload) (StructuredTool moderno).
    - Alternativa: .coroutine(**payload) (corrutina interna de la tool).
    - Fallbacks si fuera necesario.
    """
    # 1) Camino preferente
    if hasattr(calcular_cuota_hipoteca, "ainvoke"):
        return await calcular_cuota_hipoteca.ainvoke(payload)

    # 2) Corrutina interna
    coro = getattr(calcular_cuota_hipoteca, "coroutine", None)
    if coro:
        return await coro(**payload)

    # 3) Fallbacks sync (por si tu runner hace llamadas sync)
    if hasattr(calcular_cuota_hipoteca, "invoke"):
        return calcular_cuota_hipoteca.invoke(payload)

    func = getattr(calcular_cuota_hipoteca, "func", None)
    if func:
        return func(**payload)

    # 4) Último recurso: llamar directamente (si estuviera definido como función async simple)
    return await calcular_cuota_hipoteca(**payload)


@pytest.mark.asyncio
async def test_calcular_cuota_hipoteca_fija():
    """Valida cálculo en hipoteca fija usando mocks coherentes."""

    # Tu implementación espera un DICT con estas claves
    periodo_mock = {
        "days": [30] * 12,
        "year_month": [(2024, m + 1) for m in range(12)],
    }

    # Para un principal de 100k a 1 año, ponemos cuotas suficientemente altas
    # para evitar intereses negativos: 12 * 9000 = 108k
    with patch(
        "app.services.llm_service.days_in_months_for_period",
        return_value=periodo_mock,
    ), patch(
        "app.services.llm_service.calcular_cuota_mensual",
        side_effect=[9000.0, 9000.0],  # inicial, posterior
    ):
        payload = {
            "tipo_hipoteca": "fija",
            "tipo_interes_inicial": 2.5,
            "tipo_interes_posterior": 3.0,  # permitido aunque fija no lo use realmente
            "capital_prestado": 100000,
            "plazo_anos": 1,
            "comision_apertura": 0.15,
            "periodo_interes_inicial": 6,
            "euribor_inicial": 3.166,
        }

        result = await _call_tool(payload)

        # Si la tool devolviera un error, haz fallar el test con el detalle
        assert "error" not in result, f"No esperaba error. Detalle: {result}"

        assert result["cuota_inicial"] == 9000.0
        assert result["cuota_posterior"] == 9000.0
        assert result["capital_pendiente"] > 0
        assert result["importe_total_adeudado"] > 0
        assert result["intereses_totales"] >= 0


@pytest.mark.asyncio
async def test_calcular_cuota_hipoteca_variable():
    """Valida cálculo en hipoteca variable (posterior suma euríbor internamente)."""

    periodo_mock = {
        "days": [30] * 12,
        "year_month": [(2024, m + 1) for m in range(12)],
    }

    # Totales: 6 * 8000 + 6 * 9500 = 105000 → intereses positivos
    with patch(
        "app.services.llm_service.days_in_months_for_period",
        return_value=periodo_mock,
    ), patch(
        "app.services.llm_service.calcular_cuota_mensual",
        side_effect=[8000.0, 9500.0],
    ):
        payload = {
            "tipo_hipoteca": "variable",
            "tipo_interes_inicial": 2.5,
            "tipo_interes_posterior": 3.0,
            "capital_prestado": 100000,
            "plazo_anos": 1,
            "comision_apertura": 0.15,
            "periodo_interes_inicial": 6,
            "euribor_inicial": 3.166,
        }

        result = await _call_tool(payload)

        assert "error" not in result, f"No esperaba error. Detalle: {result}"

        assert result["cuota_inicial"] == 8000.0
        assert result["cuota_posterior"] == 9500.0
        assert result["capital_pendiente"] > 0
        assert result["importe_total_adeudado"] > 0
        assert result["intereses_totales"] >= 0
