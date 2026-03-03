from fastapi.testclient import TestClient
from pathlib import Path

from orchestrator.main import app
from orchestrator.core.settings import settings


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
    assert 'seguros' in use_cases
    assert use_cases['hipotecas']['routes']['cards'] == '/cards?caso_de_uso=hipotecas'
    assert use_cases['hipotecas']['label'] == 'Hipotecas'


def test_ui_shell_lists_home_and_enabled_systems():
    res = client.get('/ui/shell')
    assert res.status_code == 200
    payload = res.json()
    assert payload['schema_version'] == 'v1'
    assert payload['home']['label'] == 'HOME'
    systems = {item['id']: item for item in payload['systems']}
    assert 'hipotecas' in systems
    assert 'prestamos' in systems
    assert 'seguros' in systems
    assert systems['hipotecas']['default'] is True
    assert systems['hipotecas']['view']['system'] == 'hipotecas'
    assert systems['hipotecas']['view']['components'][0]['type'] == 'stack'


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


def test_admin_view_configs_crud_roundtrip():
    storage_path = Path(settings.VIEW_CONFIG_STORAGE_PATH)
    previous_content = storage_path.read_text(encoding='utf-8') if storage_path.exists() else None
    storage_path.write_text('[]', encoding='utf-8')

    try:
        create_payload = {
            'id': 'vista-test',
            'name': 'Vista Test',
            'system': 'hipotecas',
            'enabled': True,
            'components': [
                {'id': 'cards-main', 'type': 'cards', 'title': 'KPIs', 'data_source': '/cards', 'position': 0}
            ],
        }
        create_res = client.post('/admin/view-configs', json=create_payload)
        assert create_res.status_code == 200

        duplicate_res = client.post('/admin/view-configs', json=create_payload)
        assert duplicate_res.status_code == 409

        list_res = client.get('/admin/view-configs')
        assert list_res.status_code == 200
        assert len(list_res.json()) == 1

        get_res = client.get('/admin/view-configs/vista-test')
        assert get_res.status_code == 200
        assert get_res.json()['id'] == 'vista-test'

        create_res_2 = client.post(
            '/admin/view-configs',
            json={
                'id': 'vista-test-2',
                'name': 'Vista Test 2',
                'system': 'prestamos',
                'enabled': False,
                'components': [
                    {'id': 'txt-main', 'type': 'text', 'title': 'Notas', 'data_source': '/none', 'position': 0, 'config': {'text': 'hola'}}
                ],
            },
        )
        assert create_res_2.status_code == 200

        filtered_res = client.get('/admin/view-configs?system=hipotecas&enabled=true')
        assert filtered_res.status_code == 200
        assert len(filtered_res.json()) == 1
        assert filtered_res.json()[0]['id'] == 'vista-test'

        update_res = client.put('/admin/view-configs/vista-test', json={'name': 'Vista Test 2'})
        assert update_res.status_code == 200
        assert update_res.json()['name'] == 'Vista Test 2'

        delete_res = client.delete('/admin/view-configs/vista-test')
        assert delete_res.status_code == 204

        delete_res_2 = client.delete('/admin/view-configs/vista-test-2')
        assert delete_res_2.status_code == 204
    finally:
        if previous_content is None:
            storage_path.unlink(missing_ok=True)
        else:
            storage_path.write_text(previous_content, encoding='utf-8')


def test_admin_view_config_semantic_validation_errors():
    payload = {
        'id': 'vista-invalid',
        'name': 'Vista Invalid',
        'system': 'hipotecas',
        'enabled': True,
        'components': [
            {'id': 'cards-main', 'type': 'cards', 'title': 'KPIs', 'data_source': '/dashboard', 'position': 0}
        ],
    }
    res = client.post('/admin/view-configs', json=payload)
    assert res.status_code == 422
    assert res.json()['code'] == 'VALIDATION_ERROR'


def test_metrics_endpoint_reports_requests():
    _ = client.get('/health')
    _ = client.post('/cards?caso_de_uso=hipotecas', json={'timeRange': '24h'})
    res = client.get('/metrics')
    assert res.status_code == 200
    payload = res.json()
    assert 'requests' in payload
    assert any(item['path'] == '/health' for item in payload['requests'])


def test_admin_rate_limit_can_block_requests():
    limiter = app.state.admin_rate_limiter
    original_max = limiter.max_requests
    original_window = limiter.window_seconds
    limiter.max_requests = 1
    limiter.window_seconds = 60
    limiter.reset()

    try:
        payload = {
            'id': 'vista-rate-limit-' + __import__('uuid').uuid4().hex[:8],
            'name': 'Vista Rate Limit',
            'system': 'hipotecas',
            'enabled': True,
            'components': [
                {'id': 'cards-main', 'type': 'cards', 'title': 'KPIs', 'data_source': '/cards', 'position': 0}
            ],
        }
        first = client.post('/admin/view-configs', json=payload)
        assert first.status_code == 200

        view_id = payload['id']
        second = client.put(f'/admin/view-configs/{view_id}', json={'name': 'Vista Rate Limit v2'})
        assert second.status_code == 429

        cleanup = client.delete(f'/admin/view-configs/{view_id}')
        assert cleanup.status_code in (204, 429)
    finally:
        limiter.max_requests = original_max
        limiter.window_seconds = original_window
        limiter.reset()
        _ = client.delete(f"/admin/view-configs/{locals().get('view_id', '')}")
