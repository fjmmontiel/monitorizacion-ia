#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "config/catalog/monitor_catalog.json"
FRONT_CONFIG_DIR = ROOT / "monitorizacion-ia-front/packages/shell/src/shared/config"
FRONT_LAYOUTS_PATH = ROOT / "monitorizacion-ia-front/packages/shell/src/features/monitor/config/system_layouts.json"
BACK_USE_CASES_PATH = ROOT / "monitorizacion-ia-python/src/orchestrator/config/use_cases.yaml"


def read_catalog() -> dict[str, Any]:
    return json.loads(CATALOG_PATH.read_text(encoding="utf-8"))


def write_catalog(catalog: dict[str, Any]) -> None:
    CATALOG_PATH.write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def generate_backend_use_cases_yaml(systems: list[dict[str, Any]]) -> str:
    lines = ["use_cases:"]
    for system in systems:
        lines.extend(
            [
                f"  {system['id']}:",
                f"    adapter: {system['adapter']}",
                "    timeouts:",
                f"      ms: {system['timeout_ms']}",
            ]
        )
    return "\n".join(lines) + "\n"


def sync() -> None:
    catalog = read_catalog()
    systems = catalog.get("systems", [])
    views = catalog.get("views", [])

    front_use_cases = [
        {
            "id": item["id"],
            "label": item["label"],
            "enabled": bool(item.get("enabled", True)),
            **({"default": True} if item.get("default") else {}),
        }
        for item in systems
    ]
    write_json(FRONT_CONFIG_DIR / "use_cases.json", front_use_cases)

    front_views = [
        {
            "id": view["id"],
            "label": view["label"],
            "enabled": bool(view.get("enabled", True)),
            **({"default": True} if view.get("default") else {}),
            "components": view.get("components", ["cards", "table", "detail"]),
        }
        for view in views
    ]
    write_json(FRONT_CONFIG_DIR / "views.json", front_views)

    layouts = {
        item["id"]: {
            "id": item["id"],
            "headerTitle": item["layout"]["headerTitle"],
            "headerSubtitle": item["layout"]["headerSubtitle"],
            "sidebarTitle": item["layout"]["sidebarTitle"],
            "sidebarHint": item["layout"]["sidebarHint"],
            "tableTitle": item["layout"]["tableTitle"],
            "detailTitle": item["layout"]["detailTitle"],
            "accent": item["layout"]["accent"],
        }
        for item in systems
    }
    write_json(FRONT_LAYOUTS_PATH, layouts)

    BACK_USE_CASES_PATH.write_text(generate_backend_use_cases_yaml(systems), encoding="utf-8")


def ensure_unique_id(collection: list[dict[str, Any]], item_id: str, kind: str) -> None:
    if any(item["id"] == item_id for item in collection):
        raise SystemExit(f"{kind} with id '{item_id}' already exists")


def add_system(args: argparse.Namespace) -> None:
    catalog = read_catalog()
    systems = catalog.setdefault("systems", [])
    ensure_unique_id(systems, args.id, "System")

    if args.default:
        for item in systems:
            item["default"] = False

    systems.append(
        {
            "id": args.id,
            "label": args.label,
            "enabled": True,
            "default": args.default,
            "adapter": args.adapter,
            "timeout_ms": args.timeout_ms,
            "layout": {
                "headerTitle": f"Panel de seguimiento de {args.label.lower()}",
                "headerSubtitle": "Vista operativa generada automáticamente. Ajusta textos antes de pasar a producción.",
                "sidebarTitle": f"Filtros de {args.label.lower()}",
                "sidebarHint": "Configura criterios y aplica para refrescar resultados.",
                "tableTitle": "Historial",
                "detailTitle": "Detalle",
                "accent": args.accent,
            },
        }
    )
    write_catalog(catalog)
    sync()


def add_view(args: argparse.Namespace) -> None:
    catalog = read_catalog()
    views = catalog.setdefault("views", [])
    ensure_unique_id(views, args.id, "View")

    if args.default:
        for item in views:
            item["default"] = False

    components = [component.strip() for component in args.components.split(",") if component.strip()]
    views.append(
        {
            "id": args.id,
            "label": args.label,
            "enabled": True,
            "default": args.default,
            "components": components or ["cards", "table", "detail"],
        }
    )
    write_catalog(catalog)
    sync()


def main() -> None:
    parser = argparse.ArgumentParser(description="Manage monitor systems/views catalog and sync backend/frontend configs")
    subparsers = parser.add_subparsers(dest="command", required=True)

    sync_parser = subparsers.add_parser("sync", help="Sync generated backend/frontend configs from catalog")
    sync_parser.set_defaults(handler=lambda _args: sync())

    add_system_parser = subparsers.add_parser("add-system", help="Add a system and sync generated configs")
    add_system_parser.add_argument("--id", required=True)
    add_system_parser.add_argument("--label", required=True)
    add_system_parser.add_argument("--adapter", default="native", choices=["native", "http_proxy"])
    add_system_parser.add_argument("--timeout-ms", type=int, default=2500)
    add_system_parser.add_argument("--accent", default="#0b5fff")
    add_system_parser.add_argument("--default", action="store_true")
    add_system_parser.set_defaults(handler=add_system)

    add_view_parser = subparsers.add_parser("add-view", help="Add a monitor view and sync generated configs")
    add_view_parser.add_argument("--id", required=True)
    add_view_parser.add_argument("--label", required=True)
    add_view_parser.add_argument("--components", default="cards,table,detail")
    add_view_parser.add_argument("--default", action="store_true")
    add_view_parser.set_defaults(handler=add_view)

    args = parser.parse_args()
    args.handler(args)


if __name__ == "__main__":
    main()
