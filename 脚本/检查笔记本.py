"""Execute every notebook in a fresh kernel; save outputs outside source files."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import time

import nbformat
from nbclient import NotebookClient

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", help="Notebook files or directories relative to repository root")
    parser.add_argument("--timeout", type=int, default=180, help="Maximum seconds per code cell")
    args = parser.parse_args()
    if args.timeout <= 0:
        parser.error("timeout must be positive")
    targets = [ROOT / p for p in (args.paths or ["教材", "模板"])]
    files = set()
    for target in targets:
        if not target.exists():
            parser.error(f"Path does not exist: {target}")
        candidates = target.rglob("*.ipynb") if target.is_dir() else [target]
        for path in candidates:
            path = path.resolve()
            if not path.is_relative_to(ROOT) or path.suffix != ".ipynb":
                parser.error(f"Expected notebook within repository: {path}")
            if not any(part in {"_build", ".ipynb_checkpoints", ".venv", ".work"} for part in path.relative_to(ROOT).parts):
                files.add(path)
    if not files:
        parser.error("No notebooks found")

    output = ROOT / "_build" / "executed"
    output.mkdir(parents=True, exist_ok=True)
    results = []
    for path in sorted(files):
        relative = path.relative_to(ROOT)
        start = time.monotonic()
        record = {"path": relative.as_posix()}
        try:
            nb = nbformat.read(path, as_version=4)
            nbformat.validate(nb)
            code_cells = [c for c in nb.cells if c.cell_type == "code" and c.source.strip()]
            record["code_cells"] = len(code_cells)
            if not code_cells:
                record["status"] = "placeholder"
                print(f"PLACEHOLDER (not verified): {relative}", flush=True)
            else:
                for cell in nb.cells:
                    if cell.cell_type == "code":
                        cell.outputs = []
                        cell.execution_count = None
                    # Student metadata must not silently skip checks or permit errors.
                    cell.metadata.pop("execution", None)
                    cell.metadata["tags"] = [tag for tag in cell.metadata.get("tags", [])
                                              if tag not in {"skip-execution", "raises-exception"}]
                client = NotebookClient(
                    nb, kernel_name="python3", timeout=args.timeout,
                    allow_errors=False, force_raise_errors=True,
                    resources={"metadata": {"path": str(path.parent)}},
                )
                client.execute()
                for cell in nb.cells:
                    if cell.cell_type == "code" and cell.source.strip() and cell.execution_count is None:
                        raise RuntimeError("Nonempty code cell was not executed")
                destination = output / relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                nbformat.write(nb, destination)
                record["status"] = "passed"
                print(f"PASS: {relative}", flush=True)
        except Exception as exc:
            record.update(status="failed", error=f"{type(exc).__name__}: {exc}")
            print(f"FAIL: {relative}\n{record['error']}", file=sys.stderr, flush=True)
        record["seconds"] = round(time.monotonic() - start, 2)
        results.append(record)
    (output / "summary.json").write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    totals = {status: sum(r["status"] == status for r in results) for status in ["passed", "failed", "placeholder"]}
    print(json.dumps(totals, ensure_ascii=False), flush=True)
    print("Execution checks do not establish scientific correctness or A/B/C acceptance.")
    return int(totals["failed"] > 0)


if __name__ == "__main__":
    raise SystemExit(main())
