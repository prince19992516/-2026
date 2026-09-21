"""Regression tests: false green results would undermine the teaching workflow."""
from contextlib import redirect_stderr, redirect_stdout
import importlib.util
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

import nbformat

SPEC = importlib.util.spec_from_file_location("notebook_checks", Path(__file__).with_name("检查笔记本.py"))
CHECKS = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECKS)


class NotebookCheckTests(unittest.TestCase):
    def execute(self, cells_by_file):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            notebooks = root / "教材"
            notebooks.mkdir()
            for name, cells in cells_by_file.items():
                nbformat.write(nbformat.v4.new_notebook(cells=cells), notebooks / name)
            log = io.StringIO()
            with patch.object(CHECKS, "ROOT", root), patch.object(sys, "argv", ["check", "教材"]):
                with redirect_stdout(log), redirect_stderr(log):
                    code = CHECKS.main()
            results = json.loads((root / "_build/executed/summary.json").read_text(encoding="utf-8"))
            return code, results, log.getvalue()

    def test_tags_cannot_hide_a_failing_cell(self):
        cell = nbformat.v4.new_code_cell("raise ValueError('expected regression failure')")
        cell.metadata["tags"] = ["skip-execution", "raises-exception"]
        cell.execution_count = 1
        cell.outputs = [nbformat.v4.new_output("stream", name="stdout", text="stale success")]
        code, results, log = self.execute({"bad.ipynb": [cell]})
        self.assertEqual(code, 1, log)
        self.assertEqual(results[0]["status"], "failed")
        self.assertIn("ValueError", results[0]["error"])

    def test_each_notebook_has_a_fresh_kernel_and_empty_is_placeholder(self):
        code, results, log = self.execute({
            "01.ipynb": [nbformat.v4.new_code_cell("hidden_state = 123")],
            "02.ipynb": [nbformat.v4.new_code_cell("assert hidden_state == 123")],
            "03.ipynb": [nbformat.v4.new_markdown_cell("Pending human verification")],
        })
        self.assertEqual(code, 1, log)
        self.assertEqual([r["status"] for r in results], ["passed", "failed", "placeholder"])
        self.assertIn("NameError", results[1]["error"])


if __name__ == "__main__":
    unittest.main()
