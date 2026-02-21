"""Test"""

import pytest
from app.managers.managers import DataIntervinienteManager
from app.managers.items import EzDataInterviniente


@pytest.fixture
def interviniente_manager():
    """Test"""
    return DataIntervinienteManager()


# ==============================
# get_item
# ==============================
def test_interviniente_get_item(monkeypatch, interviniente_manager):
    """Delegación correcta a ItemManager.get_item"""
    monkeypatch.setattr(
        "app.managers.managers.ItemManager.get_item", lambda self, n: "mock_item"
    )
    res = interviniente_manager.get_item("i1")
    assert res == "mock_item"
