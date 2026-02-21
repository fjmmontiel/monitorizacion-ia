""" Modulo para test """

import pytest
from app.services.llm_service import extraer_tasas

def test_extraer_tasas_4_tasas():
    """ Modulo para test """

    texto = "Las tasas son 2,50 3,00 1,75 2,25"
    resultado = extraer_tasas(texto)
    assert resultado == [2.5, 2.5, 3.0, 1.75, 2.25] \
        or resultado == [2.5, 3.0, 1.75, 2.25]  # depende si duplica la primera

def test_extraer_tasas_menos_de_4():
    """ Modulo para test """

    texto = "Tasa inicial 1,50 y tasa final 2,00"
    resultado = extraer_tasas(texto)
    # Debe duplicar la primera tasa
    assert resultado[0] == resultado[1]
    assert len(resultado) == 3  # 2 originales + 1 duplicada

def test_extraer_tasas_formato_decimal():
    """ Modulo para test """

    texto = "Tasa especial 0,99"
    resultado = extraer_tasas(texto)
    assert resultado == [0.99, 0.99]  # Duplicada si solo hay una

