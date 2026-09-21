"""Build an executable HTML textbook using the pinned Jupyter Book 1.x toolchain."""
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def main():
    executable = Path(sys.executable).parent / ("jupyter-book.exe" if sys.platform == "win32" else "jupyter-book")
    command = str(executable) if executable.exists() else shutil.which("jupyter-book")
    if not command:
        raise SystemExit("Install 环境/requirements.txt in the active Python environment first")
    subprocess.run([command, "build", str(ROOT / "教材"), "--all", "--warningiserror", "--keep-going"],
                   cwd=ROOT, check=True)
    print(f"HTML: {ROOT / '教材/_build/html/index.html'}")


if __name__ == "__main__":
    main()
