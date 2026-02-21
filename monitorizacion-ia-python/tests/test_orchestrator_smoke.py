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


def test_cards_options_preflight_enabled():
    res = client.options(
        '/cards?caso_de_uso=hipotecas',
        headers={
            'Origin': 'http://127.0.0.1:3100',
            'Access-Control-Request-Method': 'POST',
        },
    )
    assert res.status_code == 200
    assert res.headers.get('access-control-allow-origin') == 'http://127.0.0.1:3100'


def test_datops_overview_lists_use_cases_and_routes():
    res = client.get('/datops/overview')
    assert res.status_code == 200
    payload = res.json()
    assert payload['schema_version'] == 'v1'
    use_cases = {item['id']: item for item in payload['use_cases']}
    assert 'hipotecas' in use_cases
    assert 'prestamos' in use_cases
    assert use_cases['hipotecas']['routes']['cards'] == '/cards?caso_de_uso=hipotecas'


def test_dashboard_has_operational_columns_for_hipotecas():
    res = client.post('/dashboard?caso_de_uso=hipotecas', json={'timeRange': '24h'})
    assert res.status_code == 200
    payload = res.json()
    column_keys = [column['key'] for column in payload['table']['columns']]
    assert 'fecha_hora' in column_keys
    assert 'detail' in column_keys


def test_detail_prestamos_has_multiple_panel_types():
    res = client.post('/dashboard_detail?caso_de_uso=prestamos&id=pres-100', json={'timeRange': '24h'})
    assert res.status_code == 200
    payload = res.json()
    panel_types = [panel['type'] for panel in payload['right']]
    assert 'list' in panel_types
    assert 'timeline' in panel_types
    assert 'metrics' in panel_types
