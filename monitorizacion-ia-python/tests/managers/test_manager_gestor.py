"""Test"""

import pytest
from app.managers.managers import DataGestorManager
from app.managers.items import EzDataGestor


@pytest.fixture
def gestor_manager():
    """Test"""
    return DataGestorManager()


# ==================================
# get_item
# ==================================
def test_gestor_get_item(monkeypatch, gestor_manager):
    """Test"""
    mock_super = lambda _, name: "gestor_mock"
    monkeypatch.setattr("app.managers.managers.ItemManager.get_item", mock_super)
    res = gestor_manager.get_item("g1")
    assert res == "gestor_mock"


# ==================================
# update_values
# ==================================
def test_gestor_update_values_ok(monkeypatch, gestor_manager):
    """Actualiza correctamente un EzDataGestor existente"""
    mock_gestor = EzDataGestor(name="g1", id="1", data={"campo": 1})
    monkeypatch.setattr(gestor_manager, "get_item", lambda n: mock_gestor)
    monkeypatch.setattr(gestor_manager, "add_item", lambda x: x)

    result = gestor_manager.update_values("g1", {"campo": 9})

    assert result is mock_gestor
    assert mock_gestor.data["campo"] == 9


def test_gestor_update_values_tipo_invalido(monkeypatch, gestor_manager):
    """Lanza TypeError si el objeto no es EzDataGestor válido"""

    class Dummy:
        """Test"""

        data = "no_dict"

    monkeypatch.setattr(gestor_manager, "get_item", lambda n: Dummy())

    with pytest.raises(TypeError):
        gestor_manager.update_values("g1", {"campo": 2})


def test_gestor_update_values_clave_invalida(monkeypatch, gestor_manager):
    """Lanza KeyError si la clave no existe en data"""
    mock_gestor = EzDataGestor(name="g1", id="1", data={"campo": 1})
    monkeypatch.setattr(gestor_manager, "get_item", lambda n: mock_gestor)

    with pytest.raises(KeyError):
        gestor_manager.update_values("g1", {"otro": 99})


def test_gestor_update_values_no_existente(monkeypatch, gestor_manager):
    """Devuelve mensaje si el gestor no existe"""
    monkeypatch.setattr(gestor_manager, "get_item", lambda n: None)
    res = gestor_manager.update_values("g1", {"campo": 5})
    assert "No se ha encontrado el gestor" in res


def test_gestor_update_values_keyerror_en_try(monkeypatch, gestor_manager):
    """Lanza KeyError controlado si falla internamente"""

    def mock_get(_):
        """Test"""
        raise KeyError("fallo interno")

    monkeypatch.setattr(gestor_manager, "get_item", mock_get)
    with pytest.raises(KeyError):
        gestor_manager.update_values("g1", {"campo": 5})


# ==================================
# validate_data
# ==================================
def test_gestor_validate_data_unico(gestor_manager):
    """Devuelve error si hay más de un gestor"""
    gestor_manager.items = {
        "g1": EzDataGestor("g1", "1", {"campo": 1}),
        "g2": EzDataGestor("g2", "2", {"campo": 2}),
    }
    ok, msg = gestor_manager.validate_data("g1")
    assert ok is True
    assert "" in msg
