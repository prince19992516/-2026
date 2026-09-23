"""Beginner entry point. Always use this checkout's .venv and repository root."""
from __future__ import annotations

import argparse
import http.server
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
ENV_PYTHON = ROOT / ".venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")


def run(command, label=None):
    print("执行：", label or subprocess.list2cmdline([str(x) for x in command]), flush=True)
    env = dict(os.environ, PYTHONUTF8="1", MPLBACKEND="Agg")
    process = subprocess.Popen([str(x) for x in command], cwd=ROOT, env=env)
    try:
        code = process.wait()
    except KeyboardInterrupt:
        # Ctrl+C reaches the foreground child too. Give it time to close its server.
        try:
            process.wait(timeout=10)
        except (subprocess.TimeoutExpired, KeyboardInterrupt):
            process.terminate()
            process.wait(timeout=10)
        raise
    if code:
        raise subprocess.CalledProcessError(code, command)


def require_environment():
    if not ENV_PYTHON.is_file():
        raise RuntimeError("尚未建立课程环境。请先按教程/01-环境安装与运行.md手动创建.venv、安装依赖并注册内核。")
    result = subprocess.run([str(ENV_PYTHON), "-c",
                             "import json,sys; print(json.dumps(list(sys.version_info[:2])))"],
                            capture_output=True, text=True, check=True)
    if json.loads(result.stdout) != [3, 12]:
        raise RuntimeError("现有 .venv 不是Python 3.12。请按环境教程的修复步骤重建；助手不会删除已有环境。")


def lab(port, no_browser=False):
    require_environment()
    print("此窗口将持续运行JupyterLab，保持打开是正常现象。", flush=True)
    print("在浏览器中打开Notebook，重启内核并运行全部单元，核对结果后保存。", flush=True)
    print("需要Git提交或生成教材时，请另开一个终端窗口。", flush=True)
    print("关闭浏览器不会停止服务。结束时在本窗口按Ctrl+C，等待服务关闭。", flush=True)
    command = [ENV_PYTHON, "-m", "jupyterlab", "--ip=127.0.0.1", f"--port={port}",
               "--ServerApp.answer_yes=True", f"--ServerApp.root_dir={ROOT}"]
    if no_browser:
        command.append("--no-browser")
    run(command)


def build():
    require_environment()
    executable = ENV_PYTHON.parent / ("jupyter-book.exe" if os.name == "nt" else "jupyter-book")
    if not executable.is_file():
        raise RuntimeError("课程环境缺少jupyter-book。请按教程/01-环境安装与运行.md，用.venv中的Python安装jupyter-book==1.0.4.post1和sphinx==7.4.7。")
    print("正在生成HTML教材。Notebook输出来自已保存的文件；请先在JupyterLab运行并保存。", flush=True)
    run([executable, "build", ROOT / "教材", "--all"])
    print(f"HTML: {ROOT / '教材/_build/html/index.html'}")
    command = ".\\course.cmd preview" if os.name == "nt" else "python3.12 course.py preview"
    print(f"构建完成并返回终端。运行 {command} 后，在浏览器访问 http://127.0.0.1:8000 。")


def preview(port):
    folder = ROOT / "教材/_build/html"
    if not (folder / "index.html").is_file():
        raise RuntimeError("还没有HTML教材。请先运行 build，成功后再运行 preview。")
    from functools import partial
    handler = partial(http.server.SimpleHTTPRequestHandler, directory=str(folder))
    with http.server.ThreadingHTTPServer(("127.0.0.1", port), handler) as server:
        print(f"浏览器打开：http://127.0.0.1:{port}\n此窗口持续提供教材页面；按Ctrl+C停止。", flush=True)
        server.serve_forever()


def perform(command, port=None, no_browser=False):
    try:
        if command == "lab":
            lab(port or 8888, no_browser)
        elif command == "build":
            build()
        elif command == "preview":
            preview(port or 8000)
        return 0
    except KeyboardInterrupt:
        print("\n已收到停止请求。如Jupyter仍询问是否关闭，请完成确认。")
        return 130
    except (RuntimeError, OSError, subprocess.CalledProcessError) as exc:
        print(f"\n本步未成功：{exc}\n请查看上方第一处报错；修复前不要继续下一步。", file=sys.stderr)
        print("详细说明：教程/01-环境安装与运行.md；不确定时将报错文字发给助教。", file=sys.stderr)
        return 1


def main():
    parser = argparse.ArgumentParser(description="课程助手：自动选用本仓库的Python环境，不需要手动激活。")
    parser.add_argument("command", nargs="?", choices=["lab", "build", "preview"])
    parser.add_argument("--port", type=int, help="仅lab/preview使用：指定端口")
    parser.add_argument("--no-browser", action="store_true", help="仅lab使用：不自动弹出浏览器，手动复制地址")
    args = parser.parse_args()
    if args.port is not None and (args.command not in {"lab", "preview"} or not 1 <= args.port <= 65535):
        parser.error("--port仅用于lab/preview，范围1至65535")
    if args.no_browser and args.command != "lab":
        parser.error("--no-browser仅用于lab")
    if args.command:
        return perform(args.command, args.port, args.no_browser)
    choices = {"1": "lab", "2": "build", "3": "preview"}
    while True:
        print("\n课程助手（请先按安装教程自行准备.venv）\n1 打开JupyterLab（持续占用本窗口）\n2 生成HTML教材（使用已保存内容）\n3 预览HTML教材（持续占用本窗口）\n0 退出")
        try:
            choice = input("输入数字并回车：").strip()
        except (EOFError, KeyboardInterrupt):
            return 0
        if choice == "0":
            return 0
        if choice not in choices:
            print("请输入0至3。")
            continue
        perform(choices[choice])


if __name__ == "__main__":
    raise SystemExit(main())
