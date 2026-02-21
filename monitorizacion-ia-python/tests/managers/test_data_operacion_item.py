"""Modulo para test"""

#################################################################################
###################    TESTS EzDataOperacion  ###################################
#################################################################################


import pytest
import json
from app.managers.items import EzDataOperacion
from uuid import uuid4


@pytest.fixture
def sample_data():
    """Modulo para test"""

    return {"operacion_id": 123, "importe": 100000, "plazo": 30, "tipo": "hipoteca"}


@pytest.fixture
def ez_operacion(sample_data):
    """Modulo para test"""
    identificador = str(uuid4())
    return EzDataOperacion(
        name="OperacionTest", id=identificador, data=sample_data, tab="Tab1"
    )


def test_init_sets_attributes(ez_operacion, sample_data):
    """Modulo para test"""

    assert ez_operacion.name == "OperacionTest"
    assert ez_operacion.data == sample_data
    assert ez_operacion.item_type == "DataOperacion"
    assert ez_operacion.tab == "Tab1"


def test_get_llm_str_contains_name_and_data(ez_operacion, sample_data):
    """Modulo para test"""

    llm_str = ez_operacion.get_llm_str()
    assert "## OperacionTest" in llm_str
    for key, value in sample_data.items():
        assert str(key) in llm_str
        assert str(value) in llm_str


def test_to_json_valid_and_contains_fields(ez_operacion):
    """Modulo para test"""

    json_str = ez_operacion.to_json()
    obj = json.loads(json_str)
    assert obj["id"] == ez_operacion.id
    assert obj["name"] == "OperacionTest"
    assert obj["item_type"] == "DataOperacion"
    assert obj["tab"] == "Tab1"
    assert obj["data"]["operacion_id"] == 123


def test_get_data_returns_original(ez_operacion, sample_data):
    """Modulo para test"""

    assert ez_operacion.get_data() == sample_data


def test_get_id_format(ez_operacion):
    """Modulo para test"""

    assert ez_operacion.get_id() == ez_operacion.id


def test_accepts_non_dict_data():
    """Modulo para test"""

    identificador = str(uuid4())
    data = [1, 2, 3]
    ez = EzDataOperacion(name="Lista", id=identificador, data=data)
    assert ez.get_data() == data
    # to_json should still serialize
    json_str = ez.to_json()
    obj = json.loads(json_str)
    assert obj["data"] == [1, 2, 3]
