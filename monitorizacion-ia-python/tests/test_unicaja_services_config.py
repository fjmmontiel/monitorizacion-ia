"""Modulo"""

import pytest
from app.unicaja_services_config import UnicajaServicesConfig


@pytest.fixture
def config():
    """Modulo"""

    return UnicajaServicesConfig()


def test_getters(config):
    """Modulo"""

    # Los getters deben devolver los mismos valores que los atributos
    assert config.get_client_id() == config.client_id
    assert config.get_client_secret() == config.client_secret
