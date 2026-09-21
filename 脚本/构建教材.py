"""将已保存的正文和Notebook排版成HTML；不执行Notebook代码。"""
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def main():
    executable = Path(sys.executable).parent / ("jupyter-book.exe" if sys.platform == "win32" else "jupyter-book")
    command = str(executable) if executable.exists() else shutil.which("jupyter-book")
    if not command:
        raise SystemExit("请按教程/01-环境安装与运行.md，用当前Python安装jupyter-book==1.0.4.post1和sphinx==7.4.7。")
    print("正在生成HTML教材。Notebook输出来自已保存的文件；请先在JupyterLab运行并保存。", flush=True)
    subprocess.run([command, "build", str(ROOT / "教材"), "--all"],
                   cwd=ROOT, check=True)
    print(f"HTML: {ROOT / '教材/_build/html/index.html'}")


if __name__ == "__main__":
    main()
