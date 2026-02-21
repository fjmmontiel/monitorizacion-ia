"""
Tests para DocumentoIdentidad y verificación de DNI/NIE.
Valida formatos, cálculo de letra y consulta de cliente.
"""

import pytest
from unittest.mock import patch
from app.services.verificar_dni_service import DocumentoIdentidad

PATH_SERVICE = "app.services.verificar_dni_service.ConsultaClienteService"


def test_formato_incorrecto():
    """Rechaza documentos con longitud incorrecta."""
    doc = DocumentoIdentidad("12345678")
    result = doc.verificar(segundo_interviniente=False)
    assert result["valido"] is False
    assert "formato" in result["mensaje"].lower()


def test_numero_no_valido():
    """Rechaza documentos con números no válidos."""
    doc = DocumentoIdentidad("X12A4567L")
    result = doc.verificar(segundo_interviniente=False)
    assert result["valido"] is False
    assert (
        "número" in result["mensaje"].lower() or "numero" in result["mensaje"].lower()
    )


def test_letra_incorrecta():
    """Detecta letra incorrecta en DNI/NIE."""
    doc = DocumentoIdentidad("12345678A")  # La letra no corresponde
    result = doc.verificar(segundo_interviniente=False)
    assert result["valido"] is False
    assert "letra" in result["mensaje"].lower()


def test_letra_correcta_dni():
    """Acepta un DNI válido y llama a ConsultaClienteService."""
    numeros = 12345678
    letras = "TRWAGMYFPDXBNJZSQVHLCKE"
    letra = letras[numeros % 23]
    dni = f"{numeros}{letra}"

    with patch(PATH_SERVICE) as MockConsulta:
        mock_instance = MockConsulta.return_value
        mock_instance.call.return_value = {"nombre": "Juan"}

        doc = DocumentoIdentidad(dni)
        result = doc.verificar(segundo_interviniente=False)

        assert result["valido"] is True
        assert (
            "valido" in result["mensaje"].lower()
            or "válido" in result["mensaje"].lower()
        )
        assert result["info_cliente"] == {"nombre": "Juan"}
        mock_instance.call.assert_called_once_with(dni)


def test_letra_correcta_nie():
    """Acepta un NIE válido y llama a ConsultaClienteService."""
    # X1234567? -> convertir a 01234567? para calcular letra
    numeros = int("01234567")
    letras = "TRWAGMYFPDXBNJZSQVHLCKE"
    letra = letras[numeros % 23]
    nie = f"X1234567{letra}"

    with patch(PATH_SERVICE) as MockConsulta:
        mock_instance = MockConsulta.return_value
        mock_instance.call.return_value = {"nombre": "Ana"}

        doc = DocumentoIdentidad(nie)
        result = doc.verificar(segundo_interviniente=False)

        assert result["valido"] is True
        assert (
            "valido" in result["mensaje"].lower()
            or "válido" in result["mensaje"].lower()
        )
        assert result["info_cliente"] == {"nombre": "Ana"}
        mock_instance.call.assert_called_once_with(nie)


def test_segundo_interviniente_no_consulta():
    """Si es segundo interviniente, no consulta info cliente aunque el documento sea válido."""
    numeros = 12345678
    letras = "TRWAGMYFPDXBNJZSQVHLCKE"
    letra = letras[numeros % 23]
    dni = f"{numeros}{letra}"

    with patch(PATH_SERVICE) as MockConsulta:
        doc = DocumentoIdentidad(dni)
        result = doc.verificar(segundo_interviniente=True)

        assert result["valido"] is True
        assert result.get("info_cliente") is None
        MockConsulta.return_value.call.assert_not_called()
