"""Test"""

import pytest
from app.managers.managers import DataOperacionManager
from app.managers.items import EzDataOperacion, EzDataPreeval

ATENCION_STR = "ATENCIÓN"


@pytest.fixture
def operacion_manager():
    """Test"""
    return DataOperacionManager()


# ==============================
# get_item
# ==============================
def test_operacion_get_item(monkeypatch, operacion_manager):
    """Delegación correcta a ItemManager.get_item"""
    monkeypatch.setattr(
        "app.managers.managers.ItemManager.get_item", lambda self, n: "mock_item"
    )
    res = operacion_manager.get_item("o1")
    assert res == "mock_item"


# ==============================
# validate_data
# ==============================
