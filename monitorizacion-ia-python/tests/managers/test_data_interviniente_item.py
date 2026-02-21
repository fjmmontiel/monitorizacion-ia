"""Modulo para test"""

#################################################################################
###################    TESTS EzDataInterviniente   ##############################
#################################################################################


import pytest
import json
from app.managers.items import EzDataInterviniente
from uuid import uuid4


@pytest.fixture
def sample_data():
    """Modulo para test"""

    return {"nombre": "Juan Pérez", "rol": "Titular", "edad": 35}


@pytest.fixture
def interviniente(sample_data):
    """Modulo para test"""
    id = str(uuid4())
    return EzDataInterviniente(name="Interv1", id=id, data=sample_data, tab="A")


def test_init(interviniente, sample_data):
    """Modulo para test"""

    assert interviniente.name == "Interv1"
    assert interviniente.data == sample_data
    assert interviniente.item_type == "DataInterviniente"
    assert interviniente.tab == "A"


def test_get_llm_str(interviniente):
    """Modulo para test"""

    result = interviniente.get_llm_str()
    assert "## Interv1" in result
    assert "Información del interviniente" in result
    assert "Juan Pérez" in result


def test_to_json(interviniente):
    """Modulo para test"""

    json_str = interviniente.to_json()
    obj = json.loads(json_str)
    assert obj["id"] == interviniente.id
    assert obj["name"] == "Interv1"
    assert obj["item_type"] == "DataInterviniente"
    assert obj["tab"] == "A"
    assert obj["data"]["rol"] == "Titular"


def test_get_data(interviniente, sample_data):
    """Modulo para test"""

    assert interviniente.get_data() == sample_data


def test_get_id(interviniente):
    """Modulo para test"""

    assert interviniente.get_id() == interviniente.id


def test_invalid_data():
    """Modulo para test"""

    id = str(uuid4())
    obj = EzDataInterviniente(name="Inv", id=id, data="not_a_dict")
    assert obj.get_data() == "not_a_dict"
