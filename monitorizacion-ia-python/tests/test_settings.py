""" Modulo para test """

import pytest
import yaml
from pathlib import Path
from app.settings import Settings

# -------------------
# Tests is_local
# -------------------
def test_is_local_true(monkeypatch):
    """ Modulo para test """

    monkeypatch.setenv("ENVIRONMENT", "local")
    settings = Settings()
    assert settings.is_local() is True

def test_is_local_false(monkeypatch):
    """ Modulo para test """

    monkeypatch.setenv("ENVIRONMENT", "production")
    settings = Settings()
    assert settings.is_local() is False

# -------------------
# Tests get_jwks
# -------------------
def test_get_jwks_local():
    """ Modulo para test """

    s = Settings(ENVIRONMENT="local", JWKS_LOCAL={"key": "value"})
    assert s.get_jwks() == {"key": "value"}

def test_get_jwks_local_missing():
    """ Modulo para test """

    s = Settings(ENVIRONMENT="local", JWKS_LOCAL=None)
    with pytest.raises(RuntimeError, match="JWKS_LOCAL debe estar definido en entorno local"):
        s.get_jwks()

def test_get_jwks_non_local(monkeypatch):
    """ Modulo para test """

    monkeypatch.setenv("ENVIRONMENT", "production")
    settings = Settings()
    assert settings.get_jwks() is None

# -------------------
# Tests load_from_yaml
# -------------------
def test_load_from_yaml_success(tmp_path):
    """ Modulo para test """

    config_file = tmp_path / "config.yaml"
    data = {
        "PROJECT_NAME": "TestProject",
        "ENVIRONMENT": "local",
        "PROJECT_VERSION": "1.0"
    }
    with open(config_file, "w") as f:
        yaml.safe_dump(data, f)
    
    settings = Settings.load_from_yaml(str(config_file))
    assert settings.PROJECT_NAME == "TestProject"
    assert settings.ENVIRONMENT == "local"
    assert settings.PROJECT_VERSION == "1.0"

def test_load_from_yaml_file_not_found(tmp_path):
    """ Modulo para test """

    config_file = tmp_path / "nonexistent.yaml"
    with pytest.raises(FileNotFoundError):
        Settings.load_from_yaml(str(config_file))
