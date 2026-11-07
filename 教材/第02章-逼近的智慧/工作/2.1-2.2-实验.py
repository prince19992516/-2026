# -*- coding: utf-8 -*-
"""2.1 插值与Runge现象 / 2.2 最小二乘与切比雪夫逼近 —— 本组实验脚本

运行方式（在本文件所在目录）：
    py -3.12 -m venv .venv
    .venv\\Scripts\\python.exe -m pip install numpy==1.26.4 scipy==1.14.1 matplotlib==3.9.2 threadpoolctl
    .venv\\Scripts\\python.exe 2.1-2.2-实验.py

脚本会重新打印正文中的两张对比表，并写出：
    2.1-2.2-实测摘要.txt
    图片/A2组-Runge现象.png
    图片/A2组-基函数与过拟合.png

所有计算为确定性的，除 2.2 的加噪数据固定种子 2026 外不含随机成分。
"""
import io
import sys
from pathlib import Path
import os
for _key in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[_key] = "1"

import numpy as np
from threadpoolctl import threadpool_limits
_thread_limit = threadpool_limits(limits=1)
from scipy.interpolate import BarycentricInterpolator

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BASE = Path(__file__).resolve().parent
(BASE / "图片").mkdir(exist_ok=True)
OUT = io.StringIO()


def log(s=""):
    print(s)
    OUT.write(str(s) + "\n")


def run_2_1():
    f = lambda x: 1.0 / (1.0 + 25.0 * x * x)
    grid = np.linspace(-1.0, 1.0, 4001)
    log("=== 2.1 插值与Runge现象 ===")
    log("f(x)=1/(1+25x^2), [-1,1], 4001点评价网格")
    log(f"{'n':>4} {'equidistant_max_err':>22} {'chebyshev_max_err':>20} {'ratio':>12}")
    rows = []
    for n in (5, 9, 11, 15, 21, 31):
        xe = np.linspace(-1.0, 1.0, n)
        xc = np.cos(np.pi * (2 * np.arange(n) + 1) / (2 * n))
        xc.sort()
        pe = BarycentricInterpolator(xe, f(xe), random_state=2026)(grid)
        pc = BarycentricInterpolator(xc, f(xc), random_state=2026)(grid)
        ee = float(np.max(np.abs(pe - f(grid))))
        ec = float(np.max(np.abs(pc - f(grid))))
        rows.append((n, ee, ec, ee / ec))
        log(f"{n:>4} {ee:>22.6e} {ec:>20.6e} {ee / ec:>12.4g}")

    n = 11
    xe = np.linspace(-1.0, 1.0, n)
    pe = BarycentricInterpolator(xe, f(xe), random_state=2026)
    log("")
    log(f"等距11点：节点处最大误差 = {float(np.max(np.abs(pe(xe) - f(xe)))):.1e}")
    err = np.abs(pe(grid) - f(grid))
    log(f"等距11点：区间最大误差出现在 x = {float(grid[np.argmax(err)]):.4f}")
    log(f"等距11点：x=0.95 插值 {float(pe(0.95)):.4f}，真值 {float(f(0.95)):.4f}")

    # 图 2：Runge 对比
    g = np.linspace(-1.0, 1.0, 2001)
    xc = np.cos(np.pi * (2 * np.arange(n) + 1) / (2 * n))
    xc.sort()
    pe = BarycentricInterpolator(xe, f(xe), random_state=2026)(g)
    pc = BarycentricInterpolator(xc, f(xc), random_state=2026)(g)
    fig, ax = plt.subplots(figsize=(7.2, 4.4))
    ax.plot(g, f(g), "k-", lw=2.2, label="true f(x)=1/(1+25x^2)")
    ax.plot(g, pe, "C3--", lw=1.3, label="equispaced n=11  (max err 1.92)")
    ax.plot(g, pc, "C0-.", lw=1.3, label="Chebyshev n=11  (max err 0.11)")
    ax.plot(xe, f(xe), "C3o", ms=5, label="equispaced nodes")
    ax.plot(xc, f(xc), "C0s", ms=4, mfc="none", label="Chebyshev nodes")
    ax.set_xlim(-1, 1)
    ax.set_ylim(-0.45, 2.6)
    ax.grid(alpha=0.3)
    ax.set_xlabel("x")
    ax.set_ylabel("value")
    ax.set_title("Runge phenomenon: 11 points, two node choices")
    ax.legend(fontsize=7.5, loc="upper center", ncol=2, framealpha=0.95)
    ax.axvline(0.95, color="gray", ls=":", lw=1)
    fig.tight_layout()
    fig.savefig(BASE / "图片/A2组-Runge现象.png", dpi=150)
    plt.close(fig)
    return rows


def run_2_2():
    rng = np.random.default_rng(2026)
    m = 15
    x = np.linspace(0.0, 1.0, m)
    y = np.exp(x) + rng.normal(0.0, 0.03, m)
    xt = np.linspace(0.0, 1.0, 400)

    log("")
    log("=== 2.2 最小二乘与切比雪夫逼近 ===")
    log(f"训练点 {m} 个（等距，含端点），噪声 sigma=0.03，种子 2026")
    log(f"{'deg':>4} {'cond_mono':>12} {'train_mono':>12} {'test_mono':>12} "
        f"{'cond_cheb':>11} {'train_cheb':>12} {'test_cheb':>12}")
    for d in (3, 6, 9, 12):
        V = np.vander(x, d + 1)
        c, *_ = np.linalg.lstsq(V, y, rcond=None)
        tr = float(np.max(np.abs(V @ c - y)))
        te = float(np.max(np.abs(np.vander(xt, d + 1) @ c - np.exp(xt))))
        T = np.polynomial.chebyshev.chebvander(2 * x - 1, d)
        cc, *_ = np.linalg.lstsq(T, y, rcond=None)
        trc = float(np.max(np.abs(T @ cc - y)))
        tec = float(np.max(np.abs(
            np.polynomial.chebyshev.chebvander(2 * xt - 1, d) @ cc - np.exp(xt))))
        log(f"{d:>4} {np.linalg.cond(V):>12.2e} {tr:>12.3e} {te:>12.3e} "
            f"{np.linalg.cond(T):>11.2e} {trc:>12.3e} {tec:>12.3e}")

    d = 9
    V = np.vander(x, d + 1)
    c_ls, *_ = np.linalg.lstsq(V, y, rcond=None)
    c_ne = np.linalg.solve(V.T @ V, V.T @ y)
    log("")
    log(f"正规方程 vs 直接最小二乘（d=9）：")
    log(f"  cond(V^T V) = {np.linalg.cond(V.T @ V):.2e}")
    log(f"  cond(V)     = {np.linalg.cond(V):.2e}")
    log(f"  两种解法系数最大差 = {float(np.max(np.abs(c_ls - c_ne))):.3f}")

    log("")
    log(f"{'deg':>4} {'train_max_residual':>20} {'test_max_error':>18}")
    for d in (1, 2, 3, 6, 9, 12, 14):
        V = np.vander(x, d + 1)
        c, *_ = np.linalg.lstsq(V, y, rcond=None)
        log(f"{d:>4} {float(np.max(np.abs(V @ c - y))):>20.3e} "
            f"{float(np.max(np.abs(np.vander(xt, d + 1) @ c - np.exp(xt)))):>18.3e}")

    # 图 3：条件数与过拟合
    fig, axs = plt.subplots(1, 2, figsize=(9.8, 4.0))
    deg = np.arange(1, 15)
    cm, cc = [], []
    for d in deg:
        cm.append(np.linalg.cond(np.vander(x, d + 1)))
        cc.append(np.linalg.cond(np.polynomial.chebyshev.chebvander(2 * x - 1, d)))
    axs[0].semilogy(deg, cm, "C3o-", ms=3.5, label="monomial basis")
    axs[0].semilogy(deg, cc, "C0s-", ms=3.5, label="Chebyshev basis")
    axs[0].set_xlabel("polynomial degree")
    axs[0].set_ylabel("cond of design matrix")
    axs[0].set_title("Same fit space, different conditioning")
    axs[0].grid(alpha=0.3, which="both")
    axs[0].legend(fontsize=8)
    xf = np.linspace(0, 1, 600)
    for d, color, ls, lab in (
        (3, "C0", "-", "degree 3  (test err 2.0e-2)"),
        (14, "C3", "--", "degree 14  (test err 9.7e-1)"),
    ):
        co, *_ = np.linalg.lstsq(np.vander(x, d + 1), y, rcond=None)
        axs[1].plot(xf, np.vander(xf, d + 1) @ co, ls, color=color, lw=1.5, label=lab)
    axs[1].plot(xf, np.exp(xf), "k-", lw=2.2, label="true exp(x)")
    axs[1].plot(x, y, "ko", ms=4.5, label="15 noisy training points")
    axs[1].set_xlabel("x")
    axs[1].set_ylabel("y")
    axs[1].set_ylim(-1.6, 4.2)
    axs[1].set_title("Training residual 1e-7, prediction off by 1")
    axs[1].grid(alpha=0.3)
    axs[1].legend(fontsize=7.5, loc="upper left")
    fig.tight_layout()
    fig.savefig(BASE / "图片/A2组-基函数与过拟合.png", dpi=150)
    plt.close(fig)


if __name__ == "__main__":
    np.set_printoptions(precision=6, suppress=False)
    run_2_1()
    run_2_2()
    with open(BASE / "2.1-2.2-实测摘要.txt", "w", encoding="utf-8") as fh:
        fh.write(OUT.getvalue())
    log("")
    log("已写出 2.1-2.2-实测摘要.txt 与 图片/ 下两张图")
