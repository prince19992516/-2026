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
        raise RuntimeError("尚未建立课程环境。Windows运行 .\\course.cmd setup；macOS/Linux运行 python3.12 course.py setup。")
    result = subprocess.run([str(ENV_PYTHON), "-c",
                             "import json,sys; print(json.dumps(list(sys.version_info[:2])))"],
                            capture_output=True, text=True, check=True)
    if json.loads(result.stdout) != [3, 12]:
        raise RuntimeError("现有 .venv 不是Python 3.12。请按环境教程的修复步骤重建；助手不会删除已有环境。")


def setup():
    if ENV_PYTHON.exists():
        require_environment()
        print("使用已有 .venv，补齐固定依赖；不会删除你的教材文件。", flush=True)
    else:
        if (ROOT / ".venv").exists():
            raise RuntimeError(".venv目录存在但Python不可用。请先按教程检查或重命名旧环境，勿直接覆盖。")
        if sys.version_info[:2] != (3, 12):
            raise RuntimeError("创建环境必须使用Python 3.12。Windows用 py -3.12 course.py setup；macOS/Linux用 python3.12 course.py setup。")
        run([sys.executable, "-m", "venv", ROOT / ".venv"])
    run([ENV_PYTHON, "-m", "pip", "install", "-r", ROOT / "环境/requirements.txt"])
    run([ENV_PYTHON, "-m", "ipykernel", "install", "--sys-prefix", "--name", "python3",
         "--display-name", "Python 3 (course-2026)"])
    doctor()
    print("安装完成。下一步：Windows运行 .\\course.cmd lab；macOS/Linux运行 python3.12 course.py lab。")


def doctor():
    require_environment()
    print(f"课程文件夹：{ROOT}\n课程Python：{ENV_PYTHON}", flush=True)
    code = r'''
import importlib, importlib.metadata, pathlib, sys
from jupyter_client.kernelspec import KernelSpecManager
print("Python版本：", sys.version.split()[0])
print("实际解释器：", sys.executable)
for package in ["numpy", "scipy", "matplotlib", "pandas", "sympy", "jupyterlab", "nbformat", "nbclient", "jupyter-book"]:
    print(package + "：" + importlib.metadata.version(package))
for module in ["numpy", "scipy", "matplotlib", "pandas", "sympy", "jupyterlab", "nbformat", "nbclient", "jupyter_book"]:
    importlib.import_module(module)
spec = KernelSpecManager().get_kernel_spec("python3")
if pathlib.Path(spec.argv[0]).absolute() != pathlib.Path(sys.executable).absolute():
    raise RuntimeError("python3内核未指向课程环境，请重新运行setup注册内核")
print("内核：", spec.display_name)
'''
    run([ENV_PYTHON, "-c", code], label="检查依赖版本、导入和Notebook内核")
    run([ENV_PYTHON, "-m", "pip", "check"])
    print("环境检查通过。此处未运行课程实验；运行 check 检查实验。", flush=True)


def check(paths):
    require_environment()
    for name in ["检查结构.py", "验证AI陷阱.py"]:
        run([ENV_PYTHON, ROOT / "脚本" / name])
    run([ENV_PYTHON, ROOT / "脚本/检查笔记本.py", *paths])
    print("检查命令全部结束。结果在 _build/executed/summary.json；placeholder是待完成，不是验证通过。")


def lab(port, no_browser=False):
    require_environment()
    print("此窗口将持续运行JupyterLab，保持打开是正常现象。", flush=True)
    print("请另开一个终端窗口或JupyterLab里的Terminal做检查；先保存Notebook。", flush=True)
    print("关闭浏览器不会停止服务。结束时在本窗口按Ctrl+C，等待服务关闭。", flush=True)
    command = [ENV_PYTHON, "-m", "jupyterlab", "--ip=127.0.0.1", f"--port={port}",
               "--ServerApp.answer_yes=True", f"--ServerApp.root_dir={ROOT}"]
    if no_browser:
        command.append("--no-browser")
    run(command)


def build():
    require_environment()
    run([ENV_PYTHON, ROOT / "脚本/构建教材.py"])
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


def perform(command, paths=(), port=None, no_browser=False):
    try:
        if command == "setup":
            setup()
        elif command == "doctor":
            doctor()
        elif command == "lab":
            lab(port or 8888, no_browser)
        elif command == "check":
            check(paths)
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
    parser.add_argument("command", nargs="?", choices=["setup", "doctor", "lab", "check", "build", "preview"])
    parser.add_argument("paths", nargs="*", help="仅check使用：指定章节或Notebook相对路径")
    parser.add_argument("--port", type=int, help="仅lab/preview使用：指定端口")
    parser.add_argument("--no-browser", action="store_true", help="仅lab使用：不自动弹出浏览器，手动复制地址")
    args = parser.parse_args()
    if args.paths and args.command != "check":
        parser.error("章节路径只能用于check")
    if args.port is not None and (args.command not in {"lab", "preview"} or not 1 <= args.port <= 65535):
        parser.error("--port仅用于lab/preview，范围1至65535")
    if args.no_browser and args.command != "lab":
        parser.error("--no-browser仅用于lab")
    if args.command:
        return perform(args.command, args.paths, args.port, args.no_browser)
    choices = {"1": "setup", "2": "lab", "3": "check", "4": "build", "5": "preview", "6": "doctor"}
    while True:
        print("\n课程助手\n1 安装/修复环境（首次）\n2 打开JupyterLab（持续占用本窗口）\n3 检查教材（完成后返回）\n4 构建HTML（完成后返回）\n5 预览HTML（持续占用本窗口）\n6 检查环境\n0 退出")
        try:
            choice = input("输入数字并回车：").strip()
        except (EOFError, KeyboardInterrupt):
            return 0
        if choice == "0":
            return 0
        if choice not in choices:
            print("请输入0至6。")
            continue
        perform(choices[choice])


if __name__ == "__main__":
    raise SystemExit(main())
