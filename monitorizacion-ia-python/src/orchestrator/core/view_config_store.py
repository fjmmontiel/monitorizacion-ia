import json
import os
from pathlib import Path
from threading import Lock

from orchestrator.api.schemas import ViewConfigCreate, ViewConfigUpdate, ViewConfiguration


class ViewConfigStore:
    def __init__(self, storage_path: str):
        self._path = Path(storage_path)
        self._lock = Lock()

    def list_configs(self, system: str | None = None, enabled: bool | None = None) -> list[ViewConfiguration]:
        data = self._read_raw()
        models = [ViewConfiguration.model_validate(item) for item in data]
        if system is not None:
            models = [item for item in models if item.system == system]
        if enabled is not None:
            models = [item for item in models if item.enabled is enabled]
        return models

    def get(self, view_id: str) -> ViewConfiguration:
        items = self._read_raw()
        for item in items:
            if item.get('id') == view_id:
                return ViewConfiguration.model_validate(item)
        raise KeyError(view_id)

    def create(self, payload: ViewConfigCreate) -> ViewConfiguration:
        with self._lock:
            items = self._read_raw()
            if any(item.get('id') == payload.id for item in items):
                raise ValueError(f'view_id already exists: {payload.id}')
            model = ViewConfiguration.model_validate(payload.model_dump())
            items.append(model.model_dump())
            self._write_raw(items)
        return model

    def update(self, view_id: str, payload: ViewConfigUpdate) -> ViewConfiguration:
        with self._lock:
            items = self._read_raw()
            for idx, item in enumerate(items):
                if item.get('id') != view_id:
                    continue
                merged = {**item, **payload.model_dump(exclude_unset=True)}
                model = ViewConfiguration.model_validate(merged)
                items[idx] = model.model_dump()
                self._write_raw(items)
                return model
        raise KeyError(view_id)

    def delete(self, view_id: str) -> None:
        with self._lock:
            items = self._read_raw()
            filtered = [item for item in items if item.get('id') != view_id]
            if len(filtered) == len(items):
                raise KeyError(view_id)
            self._write_raw(filtered)

    def _read_raw(self) -> list[dict]:
        if not self._path.exists():
            return []
        payload = json.loads(self._path.read_text(encoding='utf-8') or '[]')
        if not isinstance(payload, list):
            return []
        return payload

    def _write_raw(self, items: list[dict]) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._backup_current_file()

        tmp_path = self._path.with_suffix(f'{self._path.suffix}.tmp')
        payload = json.dumps(items, indent=2, ensure_ascii=False)
        tmp_path.write_text(payload, encoding='utf-8')
        os.replace(tmp_path, self._path)

    def _backup_current_file(self) -> None:
        if not self._path.exists():
            return
        backup_path = self._path.with_suffix(f'{self._path.suffix}.bak')
        backup_path.write_text(self._path.read_text(encoding='utf-8'), encoding='utf-8')
