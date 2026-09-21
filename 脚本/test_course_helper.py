"""Check novice workflow guarantees, including failure handling and real preview HTTP."""
from contextlib import redirect_stderr, redirect_stdout
import http.client
import importlib.util
import io
import os
from pathlib import Path
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

SOURCE = Path(__file__).resolve().parents[1] / "course.py"
SPEC = importlib.util.spec_from_file_location("course_helper", SOURCE)
COURSE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(COURSE)


class CourseHelperTests(unittest.TestCase):
    def test_missing_environment_gives_actionable_error(self):
        output = io.StringIO()
        with patch.object(COURSE, "ENV_PYTHON", Path("/nonexistent-course-env/python")):
            with redirect_stdout(output), redirect_stderr(output):
                result = COURSE.perform("check")
        self.assertEqual(result, 1)
        self.assertIn("setup", output.getvalue())

    def test_failed_stage_does_not_continue(self):
        with patch.object(COURSE, "require_environment"), patch.object(COURSE, "run") as run:
            run.side_effect = subprocess.CalledProcessError(1, "structure-check")
            with redirect_stderr(io.StringIO()):
                self.assertEqual(COURSE.perform("check"), 1)
            self.assertEqual(run.call_count, 1)

    def test_lab_uses_course_environment_and_explains_terminal(self):
        text = io.StringIO()
        with patch.object(COURSE, "require_environment"), patch.object(COURSE, "run") as run:
            with redirect_stdout(text):
                COURSE.lab(8890)
        command = run.call_args.args[0]
        self.assertEqual(command[0], COURSE.ENV_PYTHON)
        self.assertIn("--port=8890", command)
        self.assertIn(f"--ServerApp.root_dir={COURSE.ROOT}", command)
        self.assertIn("另开一个终端", text.getvalue())

    def test_preview_rejects_missing_build(self):
        with tempfile.TemporaryDirectory() as folder, patch.object(COURSE, "ROOT", Path(folder)):
            with self.assertRaisesRegex(RuntimeError, "先运行 build"):
                COURSE.preview(8000)

    def test_preview_serves_book_from_another_working_directory(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder) / "课程 with spaces"
            book = root / "教材/_build/html"
            book.mkdir(parents=True)
            (book / "index.html").write_text("<h1>textbook-preview-ok</h1>", encoding="utf-8")
            shutil.copyfile(SOURCE, root / "course.py")
            with socket.socket() as sock:
                sock.bind(("127.0.0.1", 0))
                port = sock.getsockname()[1]
            with tempfile.TemporaryFile() as log:
                process = subprocess.Popen([sys.executable, str(root / "course.py"), "preview", "--port", str(port)],
                    cwd=folder, stdout=log, stderr=log, env=dict(os.environ, PYTHONUTF8="1"))
                try:
                    deadline = time.monotonic() + 20
                    while True:
                        connection = http.client.HTTPConnection("127.0.0.1", port, timeout=0.5)
                        try:
                            connection.request("GET", "/")
                            response = connection.getresponse()
                            body = response.read().decode("utf-8")
                            self.assertEqual(response.status, 200)
                            self.assertIn("textbook-preview-ok", body)
                            break
                        except (ConnectionError, OSError, http.client.HTTPException):
                            if process.poll() is not None or time.monotonic() >= deadline:
                                log.seek(0)
                                self.fail(log.read().decode("utf-8", errors="replace"))
                            time.sleep(0.1)
                        finally:
                            connection.close()
                finally:
                    process.terminate()
                    process.wait(timeout=10)


if __name__ == "__main__":
    unittest.main()
