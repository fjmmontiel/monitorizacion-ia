import json
from pathlib import Path

import pytest

from orchestrator.api.schemas import ViewConfigCreate
from orchestrator.core.view_config_store import ViewConfigStore


def test_view_store_write_is_atomic_and_creates_backup(tmp_path: Path):
    storage = tmp_path / 'view_configs.json'
    storage.write_text('[]', encoding='utf-8')

    store = ViewConfigStore(str(storage))
    payload = ViewConfigCreate(
        id='vista-a',
        name='Vista A',
        system='hipotecas',
        enabled=True,
        components=[{'id': 'cards', 'type': 'cards', 'title': 'KPIs', 'data_source': '/cards', 'position': 0}],
    )

    store.create(payload)

    backup = storage.with_suffix('.json.bak')
    assert backup.exists()
    assert json.loads(storage.read_text(encoding='utf-8'))[0]['id'] == 'vista-a'


def test_view_store_semantic_validation_rejects_invalid_component(tmp_path: Path):
    storage = tmp_path / 'view_configs.json'
    storage.write_text('[]', encoding='utf-8')
    with pytest.raises(Exception):
        ViewConfigCreate(
            id='vista-invalid',
            name='Vista Invalid',
            system='hipotecas',
            enabled=True,
            components=[{'id': 'bad', 'type': 'cards', 'title': 'bad', 'data_source': '/dashboard', 'position': 0}],
        )
