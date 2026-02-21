"""Test"""

import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime

# Importa la clase a probar
from app.managers.managers import (
    RecomendacionHipotecaManager,
    EzRecomendacionHipoteca,
)


@pytest.fixture
def recomendacion_manager():
    """Test"""
    return RecomendacionHipotecaManager()


# ==================================
# get_item
# ==================================
def test_recomendacion_get_item(monkeypatch, recomendacion_manager):
    """Test"""
    mock_super = lambda _, name: "recom_mock"
    monkeypatch.setattr("app.managers.managers.ItemManager.get_item", mock_super)
    res = recomendacion_manager.get_item("r1")
    assert res == "recom_mock"


# ==================================
# update_values
# ==================================
def test_recomendacion_update_values_ok(monkeypatch, recomendacion_manager):
    """Actualiza correctamente una EzRecomendacionHipoteca existente"""
    mock_recom = EzRecomendacionHipoteca(name="r1", id="1", data={"campo": 1})
    monkeypatch.setattr(recomendacion_manager, "get_item", lambda n: mock_recom)
    monkeypatch.setattr(recomendacion_manager, "add_item", lambda x: x)

    result = recomendacion_manager.update_values("r1", {"campo": 9})

    assert result is mock_recom
    assert mock_recom.data["campo"] == 9


def test_recomendacion_update_values_tipo_invalido(monkeypatch, recomendacion_manager):
    """Lanza TypeError si el objeto no es EzRecomendacionHipoteca válido"""

    class Dummy:
        """Test"""

        data = "no_dict"

    monkeypatch.setattr(recomendacion_manager, "get_item", lambda n: Dummy())

    with pytest.raises(TypeError):
        recomendacion_manager.update_values("r1", {"campo": 5})


def test_recomendacion_update_values_clave_invalida(monkeypatch, recomendacion_manager):
    """Lanza KeyError si la clave no existe en data"""
    mock_recom = EzRecomendacionHipoteca(name="r1", id="1", data={"campo": 1})
    monkeypatch.setattr(recomendacion_manager, "get_item", lambda n: mock_recom)

    with pytest.raises(KeyError):
        recomendacion_manager.update_values("r1", {"otro": 99})


def test_recomendacion_update_values_keyerror_en_try(
    monkeypatch, recomendacion_manager
):
    """Lanza KeyError controlado si falla internamente"""

    def mock_get(_):
        """Test"""
        raise KeyError("fallo interno")

    monkeypatch.setattr(recomendacion_manager, "get_item", mock_get)
    with pytest.raises(KeyError):
        recomendacion_manager.update_values("r1", {"campo": 5})


# ==================================
# validate_data
# ==================================
def test_recomendacion_validate_data_ok(recomendacion_manager):
    """Valida datos sin errores"""
    data_solicitud = {
        "tipo_interes": ["fijo"],
        "ingresos": 3000,
        "edad": 35,
        "certificacion_energetica_vivienda": "B",
    }
    ok, msg = recomendacion_manager.validate_data(data_solicitud)
    assert ok is True
    assert msg == ""
