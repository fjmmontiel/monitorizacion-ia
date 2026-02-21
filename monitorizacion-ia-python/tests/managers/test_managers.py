"""Modulo"""

import pytest
from unittest.mock import MagicMock, patch
import pandas as pd

from app.managers import managers
from app.managers.items import EzDataPreeval

# ==== FIXTURES BÁSICAS ====


@pytest.fixture
def recomendacion_manager():
    """Modulo"""
    return managers.RecomendacionHipotecaManager()


# ==== TESTS DE ItemManager ====


def test_add_and_get_item():
    """Modulo"""
    manager = managers.ItemManager()
    fake_item = MagicMock(name="item1")
    fake_item.name = "item1"

    manager.add_item(fake_item)
    assert manager.get_item("item1") == fake_item
    assert len(manager.list_items()) == 1


def test_remove_item_notifies_observers():
    """Modulo"""
    manager = managers.ItemManager()
    observer = MagicMock()
    manager.add_observer(observer)

    item = MagicMock()
    item.name = "x"
    manager.add_item(item)
    manager.remove_item(item)

    observer.update.assert_called_with(item, "remove")
