"""Test"""

import pytest
from app.managers.managers import DataClienteManager
from app.managers.items import EzDataCliente


@pytest.fixture
def cliente_manager():
    """Test"""
    return DataClienteManager()


# ==================================
# get_item
# ==================================
def test_cliente_get_item(monkeypatch, cliente_manager):
    """Test"""
    mock_super = lambda _, name: "cliente_mock"
    monkeypatch.setattr("app.managers.managers.ItemManager.get_item", mock_super)
    res = cliente_manager.get_item("c1")
    assert res == "cliente_mock"


# ==================================
# update_values
# ==================================
def test_cliente_update_values_ok(monkeypatch, cliente_manager):
    """Actualiza correctamente un EzDataCliente existente"""
    mock_cliente = EzDataCliente(name="c1", id="1", data={"campo": 1})
    monkeypatch.setattr(cliente_manager, "get_item", lambda n: mock_cliente)
    monkeypatch.setattr(cliente_manager, "add_item", lambda x: x)

    result = cliente_manager.update_values("c1", {"campo": 5})

    assert result is mock_cliente
    assert mock_cliente.data["campo"] == 5


def test_cliente_update_values_tipo_invalido(monkeypatch, cliente_manager):
    """Lanza TypeError si el objeto no es EzDataCliente válido"""

    class Dummy:
        """Test"""

        data = "no_dict"

    monkeypatch.setattr(cliente_manager, "get_item", lambda n: Dummy())

    with pytest.raises(TypeError):
        cliente_manager.update_values("c1", {"campo": 5})


def test_cliente_update_values_clave_invalida(monkeypatch, cliente_manager):
    """Lanza KeyError si la clave no existe en data"""
    mock_cliente = EzDataCliente(name="c1", id="1", data={"campo": 1})
    monkeypatch.setattr(cliente_manager, "get_item", lambda n: mock_cliente)

    with pytest.raises(KeyError):
        cliente_manager.update_values("c1", {"otro": 99})


def test_cliente_update_values_no_existente(monkeypatch, cliente_manager):
    """Devuelve mensaje si el cliente no existe"""
    monkeypatch.setattr(cliente_manager, "get_item", lambda n: None)
    res = cliente_manager.update_values("c1", {"campo": 5})
    assert "No se ha encontrado el cliente" in res


def test_cliente_update_values_keyerror_en_try(monkeypatch, cliente_manager):
    """Lanza KeyError controlado si falla internamente"""

    def mock_get(_):
        """Test"""
        raise KeyError("fallo interno")

    monkeypatch.setattr(cliente_manager, "get_item", mock_get)
    with pytest.raises(KeyError):
        cliente_manager.update_values("c1", {"campo": 5})


# ==================================
# validate_data
# ==================================
def test_cliente_validate_data_ok(cliente_manager):
    """Test"""
    ok, msg = cliente_manager.validate_data("c1")
    assert ok is True
    assert msg == ""
