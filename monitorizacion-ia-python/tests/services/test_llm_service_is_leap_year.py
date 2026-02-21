""" Modulo para test """

import pytest
from app.services.llm_service import is_leap_year

def test_is_leap_year_true():
    """ Modulo para test """

    assert is_leap_year(2020) is True  # divisible por 4, no por 100

def test_is_leap_year_false():
    """ Modulo para test """

    assert is_leap_year(2019) is False  # no divisible por 4

def test_is_leap_year_century_false():
    """ Modulo para test """

    assert is_leap_year(1900) is False  # divisible por 100, no por 400

def test_is_leap_year_century_true():
    """ Modulo para test """

    assert is_leap_year(2000) is True  # divisible por 400
