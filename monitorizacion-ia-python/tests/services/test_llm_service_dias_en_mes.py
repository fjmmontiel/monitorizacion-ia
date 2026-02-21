""" Modulo para test """

import pytest
from datetime import datetime
from app.services.llm_service import days_in_months_for_period

def test_days_in_months_for_period_default_start(monkeypatch):
    """ Modulo para test """

    # Fuerza el año a uno no bisiesto
    fake_now = datetime(2023, 1, 1)
    monkeypatch.setattr("app.services.llm_service.datetime", type("dt", (), {"now": staticmethod(lambda: fake_now)}))
    result = days_in_months_for_period(1)
    assert len(result["days"]) == 12
    assert result["days"][1] == 28  # Febrero no bisiesto

def test_days_in_months_for_period_leap_year():
    """ Modulo para test """

    start_date = datetime(2024, 1, 1)  # 2024 es bisiesto
    result = days_in_months_for_period(1, start_date=start_date)
    assert result["days"][1] == 29  # Febrero bisiesto

def test_days_in_months_for_period_multiple_years():
    """ Modulo para test """

    start_date = datetime(2023, 12, 1)
    result = days_in_months_for_period(2, start_date=start_date)
    # Debe tener 24 meses
    assert len(result["days"]) == 24
    # El segundo febrero debe ser bisiesto (2024)
    assert result["year_month"][2][0] == 2024  # El año del tercer mes
    assert result["days"][2] == 29  # Febrero de 2024

def test_days_in_months_for_period_custom_month():
    """ Modulo para test """

    start_date = datetime(2022, 6, 1)
    result = days_in_months_for_period(1, start_date=start_date)
    assert result["year_month"][0] == (2022, 6)
    assert result["days"][0] == 30  # Junio
