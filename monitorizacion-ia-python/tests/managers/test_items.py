"""Modulo para test"""

import pytest
from unittest.mock import MagicMock
from app.managers.managers import ItemManager
from app.managers.items import ContextItem


class DummyContextItem(ContextItem):
    """Modulo para test"""

    def get_llm_str(self):
        return "dummy"

    def to_json(self):
        return {}


class DummyObserver:
    """Modulo para test"""

    def __init__(self):
        self.updates = []

    def update(self, item, change_type):
        self.updates.append((item, change_type))


@pytest.fixture
def context_item():
    """Modulo para test"""

    return ContextItem(name="item1", id="item1", data={"value": "test_value"})


@pytest.fixture
def manager():
    """Modulo para test"""

    return ItemManager()


def test_add_item_triggers_add_notification(manager):
    """Modulo para test"""

    observer = DummyObserver()
    manager.add_observer(observer)

    context_item = DummyContextItem(
        name="item1", id="item1", data={"value": "test_value"}
    )
    manager.add_item(context_item)

    assert manager.get_item("item1") == context_item
    assert observer.updates == [(context_item, "add")]


def test_add_item_existing_triggers_update_notification(manager):
    """Modulo para test"""

    observer = DummyObserver()
    manager.add_observer(observer)

    # Añadir por primera vez
    context_item = DummyContextItem(
        name="item1", id="item1", data={"value": "test_value"}
    )
    manager.add_item(context_item)
    # Añadir el mismo nombre de nuevo → debe ser update

    new_item = DummyContextItem(name="item1", id="item1", data={"value": "test_value"})
    manager.add_item(new_item)

    assert manager.get_item("item1") == new_item
    assert observer.updates == [(context_item, "add"), (new_item, "update")]


def test_remove_item_triggers_remove_notification(manager):
    """Modulo para test"""

    observer = DummyObserver()
    manager.add_observer(observer)

    context_item = DummyContextItem(
        name="item1", id="item1", data={"value": "test_value"}
    )
    manager.add_item(context_item)
    manager.remove_item(context_item)

    assert manager.get_item("item1") is None
    assert observer.updates[-1] == (context_item, "remove")


def test_remove_observer_does_not_notify(manager):
    """Modulo para test"""

    observer = DummyObserver()
    manager.add_observer(observer)
    manager.remove_observer(observer)

    context_item = DummyContextItem(
        name="item1", id="item1", data={"value": "test_value"}
    )
    manager.add_item(context_item)

    assert observer.updates == []
