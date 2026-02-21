from fastapi.testclient import TestClient

from orchestrator.main import app


client = TestClient(app)


def test_health_200():
    res = client.get('/health')
    assert res.status_code == 200
    assert res.json()['status'] == 'ok'


def test_missing_caso_de_uso_validation_error():
    res = client.post('/cards', json={'query': {}})
    assert res.status_code == 422


def test_unknown_caso_de_uso_controlled_error():
    res = client.post('/cards?caso_de_uso=no_existe', json={'query': {}})
    assert res.status_code == 404
    assert res.json()['code'] == 'UNKNOWN_CASO_DE_USO'


def test_loader_config_ok_and_native_routing():
    res = client.post('/dashboard?caso_de_uso=piloto_native', json={'query': {'limit': 1}})
    assert res.status_code == 200
    payload = res.json()
    assert payload['schema_version'] == 'v1'
    assert 'rows' in payload
