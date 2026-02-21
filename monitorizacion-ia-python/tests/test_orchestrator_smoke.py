from fastapi.testclient import TestClient

from orchestrator.main import app


client = TestClient(app)


def test_health_200():
    res = client.get('/health')
    assert res.status_code == 200
    assert res.json()['status'] == 'ok'


def test_missing_caso_de_uso_validation_error():
    res = client.post('/cards', json={'timeRange': '24h'})
    assert res.status_code == 422
    assert res.json()['code'] == 'VALIDATION_ERROR'


def test_unknown_caso_de_uso_controlled_error():
    res = client.post('/cards?caso_de_uso=no_existe', json={'timeRange': '24h'})
    assert res.status_code == 404
    assert res.json()['code'] == 'UNKNOWN_USE_CASE'


def test_loader_config_ok_and_native_routing():
    res = client.post('/dashboard?caso_de_uso=hipotecas', json={'timeRange': '24h'})
    assert res.status_code == 200
    payload = res.json()
    assert 'table' in payload
    assert 'rows' in payload['table']


def test_dashboard_detail_requires_query_id():
    res = client.post('/dashboard_detail?caso_de_uso=hipotecas', json={})
    assert res.status_code == 422
    assert res.json()['code'] == 'VALIDATION_ERROR'


def test_dashboard_detail_by_query_id_ok():
    res = client.post('/dashboard_detail?caso_de_uso=hipotecas&id=conv-001', json={'timeRange': '24h'})
    assert res.status_code == 200
    payload = res.json()
    assert 'left' in payload
    assert 'right' in payload
