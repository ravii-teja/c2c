from __future__ import annotations

import json
import mimetypes
import re
import sys
from pathlib import Path
from wsgiref.simple_server import make_server

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from workflows import run_local_filesystem_workflow


UI_ROOT = Path(__file__).resolve().parent


def _json_response(status: str, payload: dict) -> tuple[str, list[tuple[str, str]], list[bytes]]:
    body = json.dumps(payload, indent=2).encode("utf-8")
    return status, [("Content-Type", "application/json"), ("Content-Length", str(len(body)))], [body]


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _scan_payload(payload: dict[str, object]) -> dict[str, object]:
    root_path = str(payload.get("root_path", "")).strip()
    if not root_path:
        raise ValueError("A root path is required.")

    scan_root = Path(root_path).expanduser().resolve()
    if not scan_root.exists() or not scan_root.is_dir():
        raise ValueError("The selected root path does not exist or is not a directory.")

    artifact_root = str(payload.get("artifact_root", "")).strip() or str(REPO_ROOT / ".artifacts" / "ui")
    context_root_raw = str(payload.get("context_root", "")).strip()
    context_root = context_root_raw or None
    max_files = int(payload.get("max_files", 500))
    requested_extensions = payload.get("extensions") or []
    extensions = {
        extension if str(extension).startswith(".") else f".{str(extension)}"
        for extension in requested_extensions
        if str(extension).strip()
    }
    source_id = _source_id_for_path(scan_root)

    result = run_local_filesystem_workflow(
        root_path=str(scan_root),
        artifact_root=artifact_root,
        source_id=source_id,
        source_name=f"Filesystem Scan: {scan_root.name or scan_root.drive or '/'}",
        semantic_version="draft-ui-v1",
        context_root=context_root,
        include_extensions=extensions or None,
        max_files=max_files,
    )

    metadata = _read_json(result.metadata_path)
    semantic = _read_json(result.semantic_path)
    contracts = _read_json(result.contract_path)
    run_summary = _read_json(result.run_summary_path)

    assets = sorted(metadata["assets"].values(), key=lambda asset: asset["qualified_name"])
    return {
        "scan_root": str(scan_root),
        "artifact_root": artifact_root,
        "summary": {
            "asset_count": result.asset_count,
            "entity_count": result.entity_count,
            "metric_count": result.metric_count,
            "relationship_count": len(contracts.get("relationships", [])),
            "drift_event_count": result.drift_event_count,
        },
        "entities": contracts.get("entities", []),
        "metrics": contracts.get("metrics", []),
        "relationships": contracts.get("relationships", []),
        "semantic_notes": semantic.get("notes", []),
        "assets": assets,
        "run_summary": run_summary,
    }


def _source_id_for_path(path: Path) -> str:
    normalized = path.name or path.drive or "filesystem"
    return "ui-scan-" + re.sub(r"[^a-z0-9]+", "-", normalized.lower()).strip("-")


class LocalUiApplication:
    def __call__(self, environ, start_response):
        method = environ.get("REQUEST_METHOD", "GET").upper()
        path = environ.get("PATH_INFO", "/")

        if path == "/api/scan" and method == "POST":
            try:
                size = int(environ.get("CONTENT_LENGTH") or 0)
                payload = json.loads(environ["wsgi.input"].read(size).decode("utf-8") or "{}")
                status, headers, body = _json_response("200 OK", _scan_payload(payload))
            except ValueError as exc:
                status, headers, body = _json_response("400 Bad Request", {"error": str(exc)})
            except Exception as exc:  # pragma: no cover - exercised by manual UI runs.
                status, headers, body = _json_response("500 Internal Server Error", {"error": str(exc)})
            start_response(status, headers)
            return body

        if path == "/api/health":
            status, headers, body = _json_response("200 OK", {"status": "ok"})
            start_response(status, headers)
            return body

        return self._serve_static(path, start_response)

    def _serve_static(self, path: str, start_response):
        relative_path = "index.html" if path in {"", "/"} else path.lstrip("/")
        file_path = UI_ROOT / relative_path
        if not file_path.exists() or not file_path.is_file():
            status, headers, body = _json_response("404 Not Found", {"error": "Not found"})
            start_response(status, headers)
            return body

        content = file_path.read_bytes()
        content_type, _ = mimetypes.guess_type(str(file_path))
        start_response(
            "200 OK",
            [
                ("Content-Type", content_type or "text/plain; charset=utf-8"),
                ("Content-Length", str(len(content))),
            ],
        )
        return [content]


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Run the local Chaos 2 Clarity filesystem scan UI.")
    parser.add_argument("--host", default="127.0.0.1", help="Host interface to bind.")
    parser.add_argument("--port", type=int, default=8765, help="Port to bind.")
    args = parser.parse_args(argv)

    with make_server(args.host, args.port, LocalUiApplication()) as server:
        print(f"Chaos 2 Clarity UI running at http://{args.host}:{args.port}")
        server.serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
