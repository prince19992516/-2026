"""B1-丙 独立对照实现（验证者补充，非 A1/A2 原稿代码）。

覆盖：
1. 非均匀/Chebyshev 节点上的 Lagrange 插值求导；
2. 高次等距插值导数端点失效（Runge 效应）；
3. 前向/中心差分截断误差、舍入误差与最优步长；
4. 手写前向 Dual 与反向计算图 AD；
5. A1 题4、A2 题3 的关键数值核对。
"""
import json
import math
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = Path(__file__).resolve().parent
FIG = OUT.parent / "验证结果" / "图"
FIG.mkdir(parents=True, exist_ok=True)
RESULTS = {}

# ---------------------------------------------------------------- functions
def f1(x):
    return np.sin(x * x) + np.exp(x)

def f1p(x):
    return 2 * x * np.cos(x * x) + np.exp(x)

def f1pp(x):
    return 2 * np.cos(x * x) - 4 * x * x * np.sin(x * x) + np.exp(x)

def f1ppp(x):
    return -12 * x * np.sin(x * x) - 8 * x ** 3 * np.cos(x * x) + np.exp(x)

def f2(x):
    return np.exp(x) * np.cos(x)

def f2p(x):
    return np.exp(x) * (np.cos(x) - np.sin(x))

def f3(x):
    return 1.0 / (1.0 + 25.0 * x * x)

def f3p(x):
    return -50.0 * x / (1.0 + 25.0 * x * x) ** 2

def equi(n):
    return np.linspace(-1.0, 1.0, n + 1)

def cheb_zeros(n):
    k = np.arange(n + 1)
    return np.cos((2 * k + 1) * np.pi / (2 * n + 2))

def cheb_lobatto(n):
    k = np.arange(n + 1)
    return -np.cos(np.pi * k / n)

# ---------------------------------------------------------------- barycentric
def bary_weights(x):
    n = len(x)
    w = np.ones(n)
    for j in range(n):
        w[j] = 1.0 / np.prod(x[j] - np.delete(x, j))
    return w

def bary_deriv(x, y, t):
    """Derivative of the barycentric interpolant through (x, y) at t."""
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    w = bary_weights(x)
    tt = np.atleast_1d(np.asarray(t, dtype=float))
    out = np.empty_like(tt)
    for i, z in enumerate(tt):
        near = np.where(np.abs(x - z) <= 1e-12 * max(1.0, abs(z)))[0]
        if near.size:
            k = near[0]
            out[i] = sum((w[j] / w[k]) * (y[j] - y[k]) / (x[k] - x[j])
                         for j in range(len(x)) if j != k)
        else:
            u = w / (z - x)
            N = np.sum(u * y)
            S = np.sum(u)
            dN = np.sum(-u / (z - x) * y)
            dS = np.sum(-u / (z - x))
            out[i] = (dN * S - N * dS) / (S * S)
    return out[0] if np.ndim(t) == 0 else out

# ---------------------------------------------------------------- 1. interpolation derivative
interp_rows = []
grid = np.linspace(-1.0, 1.0, 4001)
for basis, gen in (("equispaced", equi),
                   ("cheb_zeros", cheb_zeros),
                   ("cheb_lobatto", cheb_lobatto)):
    for n in (4, 8, 12, 16, 20, 32):
        x = gen(n)
        for name, f, fp in (("f1=sin(x^2)+e^x", f1, f1p),
                            ("f2=e^x cos x", f2, f2p),
                            ("f3=1/(1+25x^2)", f3, f3p)):
            y = f(x)
            dgrid = bary_deriv(x, y, grid)
            interp_rows.append(dict(
                basis=basis, n=n, f=name,
                max_grid=float(np.max(np.abs(dgrid - fp(grid)))),
                max_node=float(np.max(np.abs(bary_deriv(x, y, x) - fp(x)))),
                err_x0=float(abs(bary_deriv(x, y, 0.0) - fp(0.0))),
                err_x095=float(abs(bary_deriv(x, y, 0.95) - fp(0.95))),
                err_x1=float(abs(bary_deriv(x, y, 1.0) - fp(1.0))),
            ))
RESULTS["interpolation_derivative"] = interp_rows

# figure: Runge derivative divergence
fig, ax = plt.subplots(figsize=(6.4, 4.2))
for basis, mk in (("equispaced", "o-"), ("cheb_zeros", "s-"), ("cheb_lobatto", "^-")):
    sub = [r for r in interp_rows if r["f"].startswith("f3") and r["basis"] == basis]
    ax.semilogy([r["n"] for r in sub], [r["max_grid"] for r in sub], mk, label=basis)
ax.set(xlabel="n (polynomial degree)", ylabel="max |p_n' - f'| on 4001-point grid",
       title="Derivative of interpolant, f=1/(1+25x^2)")
ax.grid(True, which="both", alpha=.25); ax.legend()
fig.tight_layout(); fig.savefig(FIG / "插值求导-Runge导数.png", dpi=160); plt.close(fig)

fig, ax = plt.subplots(figsize=(6.4, 4.2))
for basis, mk in (("equispaced", "o-"), ("cheb_lobatto", "s-")):
    sub = [r for r in interp_rows if r["f"].startswith("f1") and r["basis"] == basis]
    ax.semilogy([r["n"] for r in sub], [r["max_grid"] for r in sub], mk, label=basis)
ax.set(xlabel="n (polynomial degree)", ylabel="max |p_n' - f'| on 4001-point grid",
       title="Derivative of interpolant, f=sin(x^2)+e^x")
ax.grid(True, which="both", alpha=.25); ax.legend()
fig.tight_layout(); fig.savefig(FIG / "插值求导-光滑函数.png", dpi=160); plt.close(fig)

# ---------------------------------------------------------------- 2. finite differences
x0 = 0.7
fp0 = float(f1p(x0))
eps = np.finfo(float).eps
hs = 10.0 ** (-1.0 - np.arange(61) / 4.0)
fd_rows = []
for h in hs:
    dplus = (f1(x0 + h) - f1(x0)) / h
    d0 = (f1(x0 + h) - f1(x0 - h)) / (2 * h)
    fd_rows.append(dict(h=float(h),
                        forward=float(dplus), forward_error=float(abs(dplus - fp0)),
                        central=float(d0), central_error=float(abs(d0 - fp0))))
best_f = min(fd_rows, key=lambda r: r["forward_error"])
best_c = min(fd_rows, key=lambda r: r["central_error"])
RESULTS["finite_difference"] = dict(
    x=x0, analytic=fp0, eps=float(eps),
    best_forward_h=best_f["h"], best_forward_error=best_f["forward_error"],
    best_central_h=best_c["h"], best_central_error=best_c["central_error"],
    rows=fd_rows,
)

fig, ax = plt.subplots(figsize=(6.4, 4.2))
ax.loglog([r["h"] for r in fd_rows], [r["forward_error"] for r in fd_rows], "o-", label="forward")
ax.loglog([r["h"] for r in fd_rows], [r["central_error"] for r in fd_rows], "s-", label="central")
ax.axhline(eps, ls="--", c="grey", label="machine eps")
ax.set(xlabel="h", ylabel="absolute derivative error",
       title="F=sin(x^2)+e^x, x=0.7, float64")
ax.grid(True, which="both", alpha=.25); ax.legend()
fig.tight_layout(); fig.savefig(FIG / "差分步长-V形.png", dpi=160); plt.close(fig)

# ---------------------------------------------------------------- 3. AD (pure Python)
class Dual:
    __slots__ = ("v", "d")
    def __init__(self, v, d=0.0):
        self.v, self.d = float(v), float(d)
    def __add__(self, o):
        o = o if isinstance(o, Dual) else Dual(o)
        return Dual(self.v + o.v, self.d + o.d)
    __radd__ = __add__
    def __mul__(self, o):
        o = o if isinstance(o, Dual) else Dual(o)
        return Dual(self.v * o.v, self.d * o.v + self.v * o.d)
    __rmul__ = __mul__
    def sin(self):
        return Dual(math.sin(self.v), math.cos(self.v) * self.d)
    def cos(self):
        return Dual(math.cos(self.v), -math.sin(self.v) * self.d)
    def exp(self):
        e = math.exp(self.v)
        return Dual(e, e * self.d)

class Node:
    __slots__ = ("v", "parents", "g")
    def __init__(self, v, parents=()):
        self.v, self.parents, self.g = float(v), list(parents), 0.0

def n_add(a, b):
    return Node(a.v + b.v, ((a, 1.0), (b, 1.0)))

def n_mul(a, b):
    return Node(a.v * b.v, ((a, b.v), (b, a.v)))

def n_sin(a):
    return Node(math.sin(a.v), ((a, math.cos(a.v)),))

def n_cos(a):
    return Node(math.cos(a.v), ((a, -math.sin(a.v)),))

def n_exp(a):
    e = math.exp(a.v)
    return Node(e, ((a, e),))

def n_backward(root):
    order, seen = [], set()
    def visit(n):
        if id(n) in seen:
            return
        seen.add(id(n))
        for p, _ in n.parents:
            visit(p)
        order.append(n)
    visit(root)
    for n in order:
        n.g = 0.0
    root.g = 1.0
    for n in reversed(order):
        for p, local in n.parents:
            p.g += n.g * local
    return root

def dual_F1(x):
    x = Dual(x, 1.0)
    return (x * x).sin() + x.exp()

def dual_F2(x):
    x = Dual(x, 1.0)
    return (x * x).sin() + x * x.exp()

def reverse_F2(x):
    x = Node(x)
    v1 = n_mul(x, x)
    v2 = n_sin(v1)
    v3 = n_mul(x, n_exp(x))
    y = n_add(v2, v3)
    n_backward(y)
    return y.v, x.g

x_ad = 0.7
RESULTS["ad"] = dict(
    x=x_ad,
    F1_analytic=float(f1p(x_ad)),
    F1_dual=dual_F1(x_ad).d,
    F1_dual_error=abs(dual_F1(x_ad).d - float(f1p(x_ad))),
    F2_analytic=float(2 * x_ad * np.cos(x_ad * x_ad) + (1 + x_ad) * np.exp(x_ad)),
    F2_dual=dual_F2(x_ad).d,
    F2_reverse=reverse_F2(x_ad)[1],
    F2_reverse_error=abs(reverse_F2(x_ad)[1] - float(2 * x_ad * np.cos(x_ad * x_ad) + (1 + x_ad) * np.exp(x_ad))),
    relu_at_0=dict(left=0.0, right=1.0, comment="classical derivative does not exist at 0"),
    abs_at_0=dict(left=-1.0, right=1.0, comment="classical derivative does not exist at 0"),
)

# ---------------------------------------------------------------- 4. exercise checks
# A1 题4.2 central-difference sign
h = 0.1
D0 = (f1(x0 + h) - f1(x0 - h)) / (2 * h)
fppp = float(f1ppp(x0))
RESULTS["exercise_A1_4_2"] = dict(
    h=h, analytic=float(f1p(x0)), D0=float(D0), D0_minus_analytic=float(D0 - f1p(x0)),
    fppp=float(fppp),
    plus_h2_6_fppp=float(h * h / 6 * fppp),
    minus_h2_6_fppp=float(-h * h / 6 * fppp),
    verdict="D0-F' = +h^2/6 f''' (both are negative here); the solution's -h^2/6 is wrong",
)

# A1 题4.4 ratio
RESULTS["exercise_A1_4_4"] = dict(
    eps=float(eps), eps_pow_minus_1_6=float(eps ** (-1 / 6)),
    measured_ratio=float(best_c["h"] / best_f["h"]),
    theoretical_ratio=float(eps ** (1 / 3) / eps ** (1 / 2)),
)

# A2 题3.1 / 3.2
trap = []
for n in (4, 8, 16, 32, 64, 128):
    xs = np.linspace(0, 1, n + 1)
    T = np.trapz(xs * xs, xs)
    exact = 1.0 / 3.0
    trap.append(dict(n=n, T=float(T), abs_error=float(abs(exact - T)),
                     closed_form=float(1 / 3 + 1 / (6 * n * n))))
RESULTS["exercise_A2_3_1"] = trap

# ---------------------------------------------------------------- save
with open(OUT / "B1组-丙-实测结果.json", "w", encoding="utf-8") as fh:
    json.dump(RESULTS, fh, ensure_ascii=False, indent=2)

print(json.dumps({
    "interp_rows": len(interp_rows),
    "best_forward": (best_f["h"], best_f["forward_error"]),
    "best_central": (best_c["h"], best_c["central_error"]),
    "F1_dual_error": RESULTS["ad"]["F1_dual_error"],
    "F2_reverse_error": RESULTS["ad"]["F2_reverse_error"],
    "A1_4_2": RESULTS["exercise_A1_4_2"],
    "A1_4_4_ratio": RESULTS["exercise_A1_4_4"]["measured_ratio"],
}, ensure_ascii=False, indent=2))
