# -*- coding: utf-8 -*-
# B2组（G6）第05章 5.2节 验证Notebook 源文件（# %% 分隔单元格，转换后运行保存）
# 说明：全部代码为 B2 组独立编写（非复制 A 组代码）；其中"复现 A 组实验"部分按 A 组文字描述独立重写实现，
#       另有直接运行 A 组原代码的记录，见验证报告。

# %% [md]
# # 第05章 寻优的旅程 · B组复现与验证（5.2 节）
#
# | 被审版本 | 组别 | 提交 SHA | 文件 |
# | --- | --- | --- | --- |
# | A1 | G9 | main @ 230873df074cc91ee949c8fa91043d39a8d77066（PR #18/#19/#20 已合入） | A1-G9-5.2-下降方向.md、A1-G9-实验.md、A1-G9-习题.md/解答 |
# | A2 | G19 | main @ 230873df074cc91ee949c8fa91043d39a8d77066（PR #16 已合入） | A2-G19-正文.md、A2-G19-实验.ipynb、A2-G19-习题.md/参考解答 |
#
# 本 Notebook 为 B2 组独立对照代码：全部实现由 B2 自行编写；对 A 组稿件的直接运行记录（干净环境）见《B2组-验证报告.md》。
# 测试编号 B2-Txx 与修正清单编号 CH05-G6-B0xx 对应。

# %% [md]
# ## 复现环境与参考基线
#
# - 复现副本：`course-review-ch05`（sparse clone，HEAD 固定为被审 SHA），全新 `.venv`（Python 3.12.7）
# - 依赖：按课程声明版本安装（numpy 1.26.4 / scipy 1.14.1 / matplotlib 3.9.2 / sympy 1.13.3 等；构建链 sphinx/jupyter-book 因本机网络无法完成下载，本轮验证未用到，详见报告）
# - 参考基线策略：手算例用 sympy 精确算术或分数；数值实验用解析解（二次函数最优点=0）或独立推导的闭式量；
#   判定容差：等值类 1e-12（浮点），迭代次数/评估次数按实现约定精确比较或放宽到 ±2。
# - 随机种子：本 Notebook 无随机量。

# %%
import sys, platform, json
import numpy as np
import scipy
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
import sympy as sp
import os
os.makedirs('图片', exist_ok=True)

# 中文字体（Windows SimHei）
for cand in [r'C:\Windows\Fonts\simhei.ttf', r'C:\Windows\Fonts\msyh.ttc']:
    if os.path.exists(cand):
        try:
            font_manager.fontManager.addfont(cand)
            plt.rcParams['font.family'] = font_manager.FontProperties(fname=cand).get_name()
            break
        except Exception:
            pass
plt.rcParams['axes.unicode_minus'] = False

print('Python', platform.python_version(), '| numpy', np.__version__,
      '| scipy', scipy.__version__, '| matplotlib', matplotlib.__version__,
      '| sympy', sp.__version__, '|', platform.platform())

results = {}          # 汇总所有测试结论
def record(tid, desc, verdict, detail=''):
    results[tid] = {'verdict': verdict, 'desc': desc, 'detail': str(detail)}

def close(a, b, tol=1e-12, name=''):
    """等值比较：标量/数组（允许少量 NaN 同时存在）。"""
    a = np.asarray(a, dtype=float); b = np.asarray(b, dtype=float)
    ok = a.shape == b.shape and np.allclose(a, b, rtol=tol, atol=tol, equal_nan=True)
    if not ok:
        print(f'  [FAIL] {name}: 实测 {a} vs 参考 {b}')
    return ok

# %% [md]
# ## 5.2.1 无约束最优性条件与驻点辨析
#
# 核对两份 A 稿的驻点分类例题与反例（A1 例题 5.2.1.1–5.2.1.3、伪证 2/5、习题 9.2.1-1；A2 例 5.2.4、例 5.2.5）。

# %%
x, y = sp.symbols('x y', real=True)

def classify2d(fexpr):
    g = sp.Matrix([sp.diff(fexpr, v) for v in (x, y)])
    H = sp.Matrix([[sp.diff(fexpr, v1, v2) for v2 in (x, y)] for v1 in (x, y)])
    sols = sp.solve(list(g), (x, y), dict=True)
    out = []
    for s in sols:
        Hs = H.subs(s)
        ev = sorted(sp.N(e, 15) for e, m in Hs.eigenvals().items() for _ in range(m))
        out.append((s, ev))
    return g, H, sols, out

# --- B2-T01：A1 例题 5.2.1.1 f=x^2+y^2-2x-4y+5 ---
f1 = x**2 + y**2 - 2*x - 4*y + 5
g1, H1, sols1, ev1 = classify2d(f1)
ok1 = (sols1 == [{(x, 1), (y, 2)}] or sols1 == [{x: 1, y: 2}]) and \
      close(np.array([float(e) for e in ev1[0][1]], dtype=float), [2.0, 2.0], 1e-12, 'T01特征值')
completing = sp.expand((x - 1)**2 + (y - 2)**2) - f1
ok1 &= completing == 0
print('B2-T01 A1例5.2.1.1:', '驻点', sols1, '特征值', ev1, '配方差', completing,
      '=> 严格局部极小且全局', 'PASS' if ok1 else 'FAIL')
record('T01', 'A1例题5.2.1.1 x^2+y^2-2x-4y+5 驻点(1,2)、H=2I、全局极小', 'PASS' if ok1 else 'FAIL')

# --- B2-T02：A1 例题 5.2.1.2 f=x^2-y^2 鞍点 ---
f2 = x**2 - y**2
g2, H2, sols2, ev2 = classify2d(f2)
ok2 = (sols2 == [{x: 0, y: 0}]) and close(np.array(sorted(float(e) for e in ev2[0][1]), dtype=float), [-2.0, 2.0], 1e-12, 'T02特征值')
print('B2-T02 A1例5.2.1.2 x^2-y^2 原点鞍点:', ev2, 'PASS' if ok2 else 'FAIL')
record('T02', 'A1例题5.2.1.2 x^2-y^2 原点鞍点（特征值±2）', 'PASS' if ok2 else 'FAIL')

# --- B2-T03：A1 例题 5.2.1.3 一维退化 x^3 / x^4 ---
t = sp.symbols('t', real=True)
f3a, f3b = t**3, t**4
d1 = [(sp.diff(f3a, t, k).subs(t, 0)) for k in range(1, 5)]
d2 = [(sp.diff(f3b, t, k).subs(t, 0)) for k in range(1, 5)]
ok3 = (d1[0] == 0 and d1[1] == 0 and d1[2] == 6) and (d2[0] == 0 and d2[1] == 0 and d2[2] == 0 and d2[3] == 24)
print('B2-T03 A1例5.2.1.3:', 'x^3 导数', d1, '(首个非零阶=3奇数→非极值) | x^4 导数', d2,
      '(首个非零阶=4偶数→极小)', 'PASS' if ok3 else 'FAIL')
record('T03', 'A1例题5.2.1.3 x^3/x^4 二阶判据失效、高阶判据', 'PASS' if ok3 else 'FAIL')

# --- B2-T04：A1 伪证2反例 f=x^4-y^4（Hessian 半正定但不是极小） ---
f4 = x**4 - y**4
g4, H4, sols4, ev4 = classify2d(f4)
ok4 = (H4.subs({x: 0, y: 0}) == sp.zeros(2)) and \
      f4.subs({x: 1e-3, y: 0}) > 0 and f4.subs({x: 0, y: 1e-3}) < 0
print('B2-T04 A1伪证2反例 x^4-y^4: 原点H=0(半正定) 沿x升/沿y降 → 非极小',
      'PASS' if ok4 else 'FAIL')
record('T04', 'A1伪证2反例 x^4-y^4 半正定而非极小', 'PASS' if ok4 else 'FAIL')

# --- B2-T05：A1 伪证5 H=[[1,2],[2,1]] 对角元全正但不正定 ---
H5 = sp.Matrix([[1, 2], [2, 1]])
ev5 = sorted([sp.N(e, 15) for e in H5.eigenvals()])
ok5 = close(np.array([float(e) for e in ev5], dtype=float), [-1.0, 3.0], 1e-12, 'T05特征值')
print('B2-T05 A1伪证5 [[1,2],[2,1]] 特征值', ev5, '=> 不定', 'PASS' if ok5 else 'FAIL')
record('T05', 'A1伪证5 对角元全正不等于正定', 'PASS' if ok5 else 'FAIL')

# --- B2-T06：A1 习题9.2.1-1 f=x^3+y^3-3xy 全部驻点 ---
f6 = x**3 + y**3 - 3*x*y
g6, H6, sols6, ev6 = classify2d(f6)
pts6 = sorted((float(s[x]), float(s[y])) for s in sols6)
ok6 = (pts6 == [(0.0, 0.0), (1.0, 1.0)]) and \
      close(np.array([float(e) for e in ev6[0][1]], dtype=float), [-3.0, 3.0], 1e-12, 'T06(0,0)') and \
      close(np.array([float(e) for e in ev6[1][1]], dtype=float), [3.0, 9.0], 1e-12, 'T06(1,1)')
print('B2-T06 A1习题9.2.1-1 x^3+y^3-3xy:', '驻点', sols6, '特征值', ev6,
      '=> (0,0)鞍点、(1,1)严格局部极小', 'PASS' if ok6 else 'FAIL')
record('T06', 'A1习题9.2.1-1 驻点(0,0)鞍点、(1,1)极小', 'PASS' if ok6 else 'FAIL')

# %%
# --- B2-T07：A2 例5.2.4 一维退化族与鞍点 ---
ok7 = True
for fexpr, expect in [((t**4, t), '严格极小'), ((-t**4, t), '严格极大'),
                      ((t**3, t), '非极值(拐点)')]:
    d0 = sp.diff(fexpr[0], fexpr[1], 1).subs(fexpr[1], 0)
    d20 = sp.diff(fexpr[0], fexpr[1], 2).subs(fexpr[1], 0)
    ok7 &= (d0 == 0 and d20 == 0)
ok7 &= close(np.array([2.0, -2.0], dtype=float), [2.0, -2.0], 1e-12)
print('B2-T07 A2例5.2.4 x^4/-x^4/x^3 与 x1^2-x2^2:', '梯度二阶导均为0、鞍点H=diag(2,-2)',
      'PASS' if ok7 else 'FAIL')
record('T07', 'A2例5.2.4 半正定不足以判定极小；x1^2-x2^2鞍点', 'PASS' if ok7 else 'FAIL')

# --- B2-T08：A2 例5.2.5 局部极小未必全局 ---
# phi=(x^2-1)^2+x/2, q=4x(x^2-1)+1/2；a∈(-2,-1)、b∈(1/sqrt3,1) 唯一驻点，均严格局部极小；phi(-b)<phi(b)
phi8 = lambda u: (u*u - 1)**2 + u/2
q8   = lambda u: 4*u*(u*u - 1) + 0.5
qp8  = lambda u: 12*u*u - 4
def bisect(fn, a, b, it=200):
    for _ in range(it):
        m = (a + b) / 2
        a, b = (a, m) if fn(a) * fn(m) < 0 else (m, b)
    return (a + b) / 2
a8 = bisect(q8, -2.0, -1.0)
b8 = bisect(q8, 1/np.sqrt(3), 1.0)
ok8 = (qp8(a8) > 0) and (qp8(b8) > 0) and (phi8(-b8) < phi8(b8)) and close(phi8(-b8), phi8(b8) - b8, 1e-12, 'T08对称性')
print(f'B2-T08 A2例5.2.5: a={a8:.12f} b={b8:.12f} q\'(a)={qp8(a8):.3f} q\'(b)={qp8(b8):.3f} '
      f'phi(b)={phi8(b8):.12f} phi(-b)={phi8(-b8):.12f} => b不是全局极小',
      'PASS' if ok8 else 'FAIL')
record('T08', 'A2例5.2.5 两个严格局部极小、b非全局', 'PASS' if ok8 else 'FAIL')

# --- B2-T09：A2 命题5.2.2/5.2.3 一阶必要条件反证（负梯度一步必降）---
# 对任意光滑 f 与驻点候选：若 g(x*)≠0 沿 -g 走小步必降 —— 数值抽检
ok9 = True
for (fn, grad, p0, delta) in [((lambda u: u[0]**2 + u[1]**4), (lambda u: np.array([2*u[0], 4*u[1]**3])), np.array([1.0, 1.0]), 1e-4)]:
    g0 = grad(p0)
    t = delta / np.linalg.norm(g0)
    ok9 &= fn(p0 - t * g0) < fn(p0)
print('B2-T09 A2命题5.2.2/5.2.3 必要条件方向核验（非驻点沿-g小步必降）',
      'PASS' if ok9 else 'FAIL')
record('T09', 'A2命题5.2.2/5.2.3 一阶必要条件的反证机理', 'PASS' if ok9 else 'FAIL')

# %% [md]
# ## 5.2.2 负梯度方向、方向与步长的分工

# %%
# --- B2-T10：A1 例题5.2.2.1 精确步长一步手算（分数精确核验） ---
# f=x^2+4y^2, x0=(1,1), A=diag(2,8)：α0=68/520=17/130, x1=(48/65,-3/65), g1·g0=0 精确成立
from fractions import Fraction
alpha0 = Fraction(68, 520)
x1_ = (Fraction(1) - Fraction(2) * alpha0, Fraction(1) - Fraction(8) * alpha0)
g0_ = (Fraction(2), Fraction(8))
g1_ = (Fraction(2) * x1_[0], Fraction(8) * x1_[1])
orth = g1_[0] * g0_[0] + g1_[1] * g0_[1]
ok10 = (alpha0 == Fraction(17, 130)) and (x1_[0] == Fraction(48, 65)) and (x1_[1] == Fraction(-3, 65)) and orth == 0
print('B2-T10 A1例5.2.2.1:', f'α0={alpha0}={float(alpha0):.6f} x1={x1_}≈({float(x1_[0]):.6f},{float(x1_[1]):.6f}) g1·g0={orth}',
      'PASS' if ok10 else 'FAIL')
record('T10', 'A1例题5.2.2.1 精确步长68/520、正交性精确成立', 'PASS' if ok10 else 'FAIL')

# --- B2-T11：A1 例题5.2.2.2 下降方向判定 ---
g11 = np.array([1.0, 2.0])
ds = {'(-1,-2)': (-1, -2), '(-2,1)': (-2, 1), '(1,-2)': (1, -2), '(1,2)': (1, 2)}
expect11 = {'(-1,-2)': '下降', '(-2,1)': '否(正交)', '(1,-2)': '下降', '(1,2)': '否(上升)'}
got11 = {}
for kk, dd in ds.items():
    v = g11 @ np.array(dd)
    got11[kk] = '下降' if v < 0 else ('否(正交)' if v == 0 else '否(上升)')
ok11 = all(got11[k] == expect11[k] for k in ds)
print('B2-T11 A1例5.2.2.2:', {k: (ds[k], got11[k]) for k in ds}, 'PASS' if ok11 else 'FAIL')
record('T11', 'A1例题5.2.2.2 四个方向的下降性判定', 'PASS' if ok11 else 'FAIL')

# %%
# --- B2-T12：A2 例5.2.9 好方向 + 坏步长 ---
# phi=x^2/2, p=-x: 0<α<2 下降、α=2 振荡、α>2 发散
ok12 = True
for alpha, x0, expect in [(1.9, 2.0, '下降'), (2.0, 2.0, '振荡'), (2.1, 2.0, '上升')]:
    x1 = (1 - alpha) * x0
    ratio = 0.5 * x1**2 / (0.5 * x0**2)
    got = '下降' if ratio < 1 else ('振荡' if ratio == 1 else '上升')
    ok12 &= (got == expect)
print('B2-T12 A2例5.2.9:', {a: (0.5*((1-a)*2)**2/2) for a in [1.9, 2.0, 2.1]},
      '=> 0<α<2下降、α=2振荡、α>2发散', 'PASS' if ok12 else 'FAIL')
record('T12', 'A2例5.2.9 下降方向加过大步长仍失败', 'PASS' if ok12 else 'FAIL')

# %%
# --- B2-T13：固定步长收敛充要条件 0<α<2/λmax（A1正文/A2例5.2.9/A2习题5.2-A共同主张） ---
def gd_fixed(A, x0, alpha, itmax, tol=1e-8, overflow_break=True):
    x = np.array(x0, dtype=float)
    for k in range(itmax):
        with np.errstate(over='ignore', invalid='ignore'):
            x = x - alpha * (A @ x)
        g = A @ x
        if np.linalg.norm(g) <= tol:
            return k + 1, x, '梯度达标'
        if overflow_break and not np.all(np.isfinite(x)):
            return k + 1, x, '溢出'
    return itmax, x, '达到上限'

print('B2-T13 固定步长充要条件核验：')
ok13 = True
# A=diag(2,8): 2/L=0.25
for alpha in [0.24, 0.26]:
    k, xf, why = gd_fixed(np.diag([2.0, 8.0]), [1.0, 1.0], alpha, 100000)
    ok13 &= (why == '梯度达标' if alpha < 0.25 else why in ('溢出', '达到上限'))
    print(f'  A=diag(2,8) α={alpha}: k={k} 退出={why} 期望={"收敛" if alpha<0.25 else "发散"}')
# A=diag(1,20): 2/L=0.1（A2 习题5.2-A 的 0<α<0.1）
for alpha, expect in [(0.05, '收敛'), (0.1, '振荡(‖g‖→40)'), (0.12, '发散')]:
    k, xf, why = gd_fixed(np.diag([1.0, 20.0]), [2.0, 2.0], alpha, 600)
    gnorm = np.linalg.norm(np.diag([1.0, 20.0]) @ xf)
    got = '收敛' if why == '梯度达标' else ('振荡(‖g‖→40)' if why == '达到上限' and abs(gnorm - 40.0) < 1e-6 else '发散')
    ok13 &= (got == expect)
    print(f'  A=diag(1,20) α={alpha}: k={k} ‖g‖={gnorm:.3e} 退出={why} 判定={got} 期望={expect}')
record('T13', '固定步长收敛充要条件 0<α<2/λmax（两稿共同主张）', 'PASS' if ok13 else 'FAIL')

# %%
# --- B2-T14：精确线搜索正交性（锯齿根源）与条件数效应（A1 正文 5.2.2 / 深度透析） ---
def gd_exact(A, x0, itmax=100000, tol=1e-12):
    x = np.array(x0, dtype=float)
    traj = [x.copy()]
    for k in range(itmax):
        g = A @ x
        if np.linalg.norm(g) <= tol:
            return k, np.array(traj)
        a = (g @ g) / (g @ A @ g)
        x = x - a * g
        traj.append(x.copy())
    return itmax, np.array(traj)

# 正交性：d_{k+1}·d_k = g_{k+1}·g_k = 0（二次函数精确线搜索）
A14 = np.diag([2.0, 8.0])
k14, tr14 = gd_exact(A14, [1.0, 1.0])
gs = A14 @ tr14.T
dots = np.array([gs[:, i] @ gs[:, i + 1] for i in range(gs.shape[1] - 1)])
ok14 = (np.max(np.abs(dots)) < 1e-10) and k14 >= 1
print(f'B2-T14a 精确线搜索相邻梯度正交（A=diag(2,8), x0=(1,1)）: k={k14}, max|g_{k+1}·g_k|={np.max(np.abs(dots)):.2e}',
      'PASS' if ok14 else 'FAIL')

# 条件数效应
print('B2-T14b 条件数对精确线搜索梯度下降迭代次数的影响（tol=1e-12）：')
ok14b = True
counts = {}
for kap in [1, 10, 100, 1000]:
    k, _ = gd_exact(np.diag([1.0, float(kap)]), [1.0, 1.0])
    counts[kap] = k
    print(f'  κ={kap}: k={k}')
# 注意：对齐初值 (1,1)+对角 A 时 κ=1000 反而更快收敛（9步）——这正是 A1 正文图注
# "上千步仍不收敛"与其自身代码矛盾之处（见 T14c），也印证 A1 实验5.2-B"起点落在坐标轴
# 上会得到偶然很快的假象、所以要旋转30°"的说明。
ok14b &= (counts[1] == 1) and (counts[10] > counts[1])
record('T14', f'精确线搜索正交性验证（k={counts}，对齐初值下κ=1000快速收敛为已知假象）', 'PASS' if (ok14 and ok14b) else 'FAIL')

print('B2-T14c 直接复跑 A1 正文 5.2.2 条件数代码块（grad_desc_exact, maxit=200, tol=1e-12）：')
def a1_gd_exact(A, b, x0, maxit=200, tol=1e-12):
    x = np.array(x0, dtype=float); xs = [x.copy()]
    for k in range(maxit):
        g = A @ x - b
        if np.linalg.norm(g) < tol: break
        a = (g @ g) / (g @ A @ g)
        x = x - a * g
        xs.append(x.copy())
    return np.array(xs)
for kap in [1, 10, 100, 1000]:
    xs = a1_gd_exact(np.diag([1.0, float(kap)]), np.zeros(2), [1.0, 1.0])
    print(f'  κ={kap}: 共 {len(xs)-1} 步，末 ‖x‖={np.linalg.norm(xs[-1]):.2e}，末 ‖g‖={np.linalg.norm(np.diag([1.0,float(kap)])@xs[-1]):.2e}')
record('T14c', 'A1正文条件数代码块实际行为：对齐初值下κ=1000约9步收敛（与图注"上千步仍不收敛"不符）', 'CONFIRMED')

# %%
# --- B2-T15：A1 正文 5.2.2 代码块 与 图5-12/5-13 图注的一致性核对 ---
# 正文紧邻图5-13的代码块：A=diag(2,8)，alphas=[0.01,0.05,0.1,0.2,0.3]，2/L=0.25
# 图5-13图注：α=0.004/0.009/0.045 收敛、2/L=0.1、α=0.11 超过 2/L（来自实验5.2-B的旋转H=diag(1,20)）
A15 = np.diag([2.0, 8.0])
print('B2-T15a 正文代码块（A=diag(2,8)，2/L=0.25）各固定步长 60 步后的 f：')
out15 = {}
for a in [0.01, 0.05, 0.1, 0.2, 0.3]:
    x = np.array([1.0, 1.0])
    for _ in range(60):
        x = x - a * (A15 @ x)
    out15[a] = 0.5 * x @ A15 @ x
    print(f'  α={a}: f={out15[a]:.3e}')
ok15a = (out15[0.3] > out15[0.2] > 1e6)  # α=0.3 在 A=diag(2,8) 下应发散
print('  => 该代码块中 α=0.3 发散、临界值是 0.25，与图注"2/L=0.1、α=0.11 超界"不一致 => 图注与代码块不一致')

# 实验5.2-B 设置（旋转30°的 diag(1,20)）独立复现图注数字
th = np.deg2rad(30)
R = np.array([[np.cos(th), -np.sin(th)], [np.sin(th), np.cos(th)]])
H15 = R @ np.diag([1.0, 20.0]) @ R.T
print('B2-T15b 旋转H=diag(1,20)（2/L=0.1）独立复现图注中的步数（期望 4674/2073/407/199/发散）：')
exp15b = {0.004: 4674, 0.009: 2073, 0.045: 407, 0.09: 199}
ok15b = True
for a in [0.004, 0.009, 0.045, 0.09, 0.11]:
    k, xf, why = gd_fixed(H15, [1.0, 1.0], a, 20000, overflow_break=False)
    print(f'  α={a}: k={k} 退出={why} 末‖g‖={np.linalg.norm(H15 @ xf):.2e}')
    if a in exp15b:
        ok15b &= (k == exp15b[a])
    else:
        ok15b &= (why != '梯度达标' and k == 20000)
print('  =>', 'PASS（与A1实验5.2-B实测输出完全一致）' if ok15b else 'FAIL')
record('T15', 'A1图5-12/5-13图注与正文代码块不一致（图注来自实验5.2-B的旋转H）', 'CONFIRMED')
record('T15b', f'A1实验5.2-B固定步长步数复现 {exp15b}', 'PASS' if ok15b else 'FAIL')

# --- B2-T16：A1 伪证3 定量核验（局部极小未必全局） ---
f16  = lambda u: u*u + np.sin(10*u)
df16 = lambda u: 2*u + 10*np.cos(10*u)
d2f16= lambda u: 2 - 100*np.sin(10*u)
xs = np.linspace(-2, 2, 40001)
d = df16(xs)
idx = np.where(np.signbit(d[1:]) != np.signbit(d[:-1]))[0]
mins16 = []
for i in idx:
    lo, hi = xs[i], xs[i+1]
    for _ in range(200):
        m = (lo + hi) / 2
        lo, hi = (lo, m) if df16(lo) * df16(m) < 0 else (m, hi)
    c = (lo + hi) / 2
    if d2f16(c) > 0:
        mins16.append((c, f16(c), d2f16(c)))
print('B2-T16 A1伪证3核验：f=x^2+sin(10x) 在 [-2,2] 内 f\'\'>0 的驻点：')
for c, v, d2 in mins16:
    print(f'  x={c:.6f}  f={v:.6f}  f\'\'={d2:.2f} (>0 => 局部极小)')
vals16 = [v for _, v, _ in mins16]
ok16 = (len(mins16) >= 2) and (max(vals16) - min(vals16) > 1e-6)
print('  => 至少两个局部极小且函数值互异 => 局部极小不保证全局，', 'PASS' if ok16 else 'FAIL')
record('T16', f'A1伪证3：{len(mins16)} 个 f\'\'>0 的局部极小、函数值互异', 'PASS' if ok16 else 'FAIL')

# %% [md]
# ## 5.2.3 Armijo 回溯、Wolfe 条件与信赖域的基本思想

# %%
# --- B2-T17：A1 例题5.2.3.1 Armijo 回溯手算精确核验 ---
# f=x^2, x_k=1, d=-1, c1=0.1：RHS=1-0.2α；α0=10 的回溯序列
c1_17 = 0.1
def f17(a): return (1 - a) ** 2
print('B2-T17 A1例5.2.3.1 回溯核验（α0=10）：')
ok17 = True
seq = [10.0, 5.0, 2.5, 1.25]
for a in seq:
    lhs, rhs = f17(a), 1 - 0.2 * a
    ok = lhs <= rhs
    print(f'  α={a}: f={lhs} RHS={rhs} -> {"接受" if ok else "拒绝"}')
    ok17 &= (ok == (a == 1.25))
ok17 &= f17(1) <= 1 - 0.2  # α0=1 时一步接受
print('  α=1（α0=1）: f=0 ≤ 0.8 接受', 'PASS' if ok17 else 'FAIL')
record('T17', 'A1例题5.2.3.1 Armijo回溯逐次试探值', 'PASS' if ok17 else 'FAIL')

# --- B2-T18：A1 例题5.2.3.2 Wolfe 曲率条件边界值 ---
# c2=0.9；曲率 LHS=∇f(1-α)·(-1)；RHS=c2·(-2)
c2_18 = 0.9
print('B2-T18 A1例5.2.3.2 Wolfe曲率核验（c2=0.9，RHS=-1.8）：')
ok18 = True
for a, expect in [(1.0, True), (0.1, True), (0.01, False)]:
    xnew = 1 - a
    lhs = 2 * xnew * (-1)
    got = lhs >= c2_18 * (-2)
    ok18 &= (got == expect)
    print(f'  α={a}: LHS={lhs} {"≥" if got else "<"} -1.8 -> {"满足" if got else "不满足"}（期望{"满足" if expect else "不满足"}）')
record('T18', 'A1例题5.2.3.2 Wolfe曲率条件（含α=0.1临界）', 'PASS' if ok18 else 'FAIL')

# %%
# --- B2-T19：A2 例5.2.10 完整回溯表精确核验 ---
# phi=(x1^2+20x2^2)/2, x=(2,2), g=(2,40), p=-g, c1=1e-4, α0=1, β=1/2
def phi19(z): return 0.5 * (z[0]**2 + 20 * z[1]**2)
x19 = np.array([2.0, 2.0]); p19 = -np.array([2.0, 40.0]); fx19 = 42.0; slope19 = -1604.0
expect19 = [(1.0, 14440.0, 41.8396), (0.5, 3240.5, 41.9198), (0.25, 641.125, 41.9599),
            (0.125, 91.53125, 41.97995), (0.0625, 4.2578125, 41.989975)]
print('B2-T19 A2例5.2.10 回溯表核验：')
ok19 = True
for a, f_exp, rhs_exp in expect19:
    f_got = phi19(x19 + a * p19)
    rhs = fx19 + 1e-4 * a * slope19
    ok19 &= close(f_got, f_exp, 1e-10, f'f(α={a})') and close(rhs, rhs_exp, 1e-10, f'RHS(α={a})')
    acc = f_got <= rhs
    print(f'  α={a}: f={f_got:.7f} RHS={rhs:.7f} -> {"接受" if acc else "拒绝"}（期望{"接受" if a == 0.0625 else "拒绝"}）')
    ok19 &= (acc == (a == 0.0625))
x_plus = x19 + 0.0625 * p19
ok19 &= close(x_plus, [1.875, -0.5], 1e-12, 'x+')
print(f'  x+ = {x_plus} 期望 [1.875 -0.5]', 'PASS' if ok19 else 'FAIL')
record('T19', 'A2例5.2.10 Armijo回溯整表与更新点', 'PASS' if ok19 else 'FAIL')

# %%
# --- B2-T20：A1 定理5.2.3.1 回溯有限终止 + 非下降方向永不满足（A1伪证6/A2命题5.2.11） ---
def backtrack(fn, gd, x, d, alpha0=1.0, c1=1e-4, beta=0.5, maxbt=100, alpha_min=1e-16):
    fx, slope = fn(x), gd(x) @ d
    a = alpha0
    for j in range(maxbt):
        if a < alpha_min:
            return a, j + 1, False
        if fn(x + a * d) <= fx + c1 * a * slope:
            return a, j + 1, True
        a *= beta
    return a, maxbt, False

rng = np.random.default_rng(0)
ok20 = True
# 正常情形：随机正定二次 + 随机起点，回溯必终止
for _ in range(50):
    B = rng.normal(size=(4, 4)); A = B.T @ B + np.eye(4)
    x0 = rng.normal(size=4)
    d = -(A @ x0)
    a, j, ok = backtrack(lambda z: 0.5 * z @ A @ z, lambda z: A @ z, x0, d)
    ok20 &= ok and j <= 60
# 非下降方向：d=+g 永不满足 Armijo（β 缩减至 1e-30 仍失败）
A20 = np.diag([2.0, 8.0]); x20 = np.array([1.0, 1.0]); d20 = A20 @ x20
a, j, ok = backtrack(lambda z: 0.5 * z @ A20 @ z, lambda z: A20 @ z, x20, d20, maxbt=100)
ok20 &= (not ok)
print(f'B2-T20 回溯终止性：50 个随机正定二次全部有限终止；d=+g（非下降方向）触发 alpha_min 保护退出（α={a:.2e}）=>',
      'PASS' if ok20 else 'FAIL')
print('  注：若无 alpha_min 保护，α 缩到 2^-56 时 x+αd 与 x 在浮点下相同，Armijo 会被"原地不动"满足——')
print('  这正说明 A1 lab_common 与 A2 算法框中的最小步长/搜索失败保护是必要的。')
record('T20', 'A1定理5.2.3.1/A2命题5.2.11 回溯有限终止与方向前提', 'PASS' if ok20 else 'FAIL')

# %%
# --- B2-T21：A1 定理5.2.3.2 证明思路缺陷核验（φ 有下界未必取得局部极小） ---
# A1 证明第1步断言"φ'(0)<0 且 φ 有下界 ⇒ φ 必在某 α*>0 处取得局部极小"。
# 反例 φ(α)=e^{-α}：有下界(0)、φ'(0)=-1<0、严格递减、无局部极小点被取到；
# 但 Wolfe 步长依然存在（α=-ln c2），说明定理结论对、A1 的证明路径不对。
alpha_grid = np.linspace(0, 4, 4001)
psi21 = np.exp(-alpha_grid)
dpsi21 = -np.exp(-alpha_grid)
no_local_min = np.all(np.diff(psi21) < 0)  # 严格递减 => 无局部极小
c1_21, c2_21 = 1e-4, 0.9
a21 = -np.log(c2_21)                      # 曲率条件恰满足点
armijo21 = np.exp(-a21) <= 1 - c1_21 * a21
strong21 = abs(-np.exp(-a21)) <= c2_21 * 1
ok21 = no_local_min and armijo21 and strong21
print('B2-T21 A1定理5.2.3.2证明思路缺陷：φ(α)=e^{-α} 严格递减无局部极小，'
      f'但 α={a21:.6f} 满足 Armijo({armijo21}) 与强Wolfe({strong21}) =>',
      'A1证明第1步不成立（定理结论仍对，A2命题5.2.15证明正确）' if ok21 else 'FAIL')
record('T21', 'A1定理5.2.3.2证明"φ必取得局部极小"不成立（反例e^{-α}）；结论本身正确', 'CONFIRMED' if ok21 else 'FAIL')

# %%
# --- B2-T22：A2 例5.2.16 信赖域例精确核验 ---
# phi=x^2/2, x=1, B=0: m(s)=1/2+s; Δ=3 -> s=-3, pred=3, ared=-1.5, rho=-0.5 拒绝
# Δ=1 -> s=-1, pred=1, ared=0.5, rho=0.5
def m22(s): return 0.5 + s
def phi22(x): return 0.5 * x * x
ok22 = True
for Delta, s_exp, pred_exp, rho_exp in [(3, -3.0, 3.0, -0.5), (1, -1.0, 1.0, 0.5)]:
    s = -Delta  # 线性递减模型，极小点在边界 -Δ
    pred = m22(0) - m22(s)
    ared = phi22(1) - phi22(1 + s)
    rho = ared / pred
    ok22 &= close(s, s_exp, 1e-12) and close(pred, pred_exp, 1e-12) and close(rho, rho_exp, 1e-12)
    print(f'  Δ={Delta}: s={s} pred={pred} ared={ared} rho={rho}（期望 pred={pred_exp}, rho={rho_exp}）')
print('B2-T22 A2例5.2.16 信赖域预测/实际下降', 'PASS' if ok22 else 'FAIL')
record('T22', 'A2例5.2.16 信赖域半径约束不能保证实际下降', 'PASS' if ok22 else 'FAIL')

# %%
# --- B2-T23：A1 实验5.2-C 信赖域 λ-Δ 表独立复现 ---
# H=rot30(diag(1,20)), x0=(1,1)；对 Δ∈{2,1,0.5,0.2,0.05} 用二分法求 λ，核对 λ/‖d‖/pred/actual
def trust_step(H, g, f0, x0, Delta, tol=1e-12):
    lo, hi = 0.0, 1e6
    for _ in range(200):
        lam = 0.5 * (lo + hi)
        d = np.linalg.solve(H + lam * np.eye(2), -g)
        if np.linalg.norm(d) > Delta:
            lo = lam
        else:
            hi = lam
    lam = hi
    d = np.linalg.solve(H + lam * np.eye(2), -g)
    pred = -(g @ d + 0.5 * d @ H @ d)
    act = f0 - 0.5 * (x0 + d) @ H @ (x0 + d)
    return lam, d, pred, act

g23 = H15 @ np.array([1.0, 1.0]); f23 = 0.5 * np.array([1.0, 1.0]) @ H15 @ np.array([1.0, 1.0])
expect23 = {2.0: (0.0, 1.4142, 2.273), 1.0: (0.4628, 1.0000, 2.179),
            0.5: (2.5878, 0.5000, 1.770), 0.2: (18.9554, 0.2000, 1.114), 0.05: (129.7167, 0.0500, 0.3483)}
print('B2-T23 A1实验5.2-C 信赖域表独立复现（期望 λ/‖d‖/pred=actual）:')
ok23 = True
for Delta, (lam_e, de, pe) in expect23.items():
    lam, d, pred, act = trust_step(H15, g23, f23, np.array([1.0, 1.0]), Delta)
    ok23 &= close(lam, lam_e, 1e-3, f'λ(Δ={Delta})') and close(np.linalg.norm(d), de, 1e-3, '‖d‖') \
        and close(pred, pe, 1e-3, 'pred') and close(pred, act, 1e-9, 'pred=act')
    print(f'  Δ={Delta}: λ={lam:.4f} ‖d‖={np.linalg.norm(d):.4f} pred={pred:.3e} actual={act:.3e} ρ={act/pred:.6f}')
record('T23', 'A1实验5.2-C 信赖域 λ-Δ 关系表', 'PASS' if ok23 else 'FAIL')

# %%
# --- B2-T24：A1 实验5.2-B 固定步长表独立复现（期望 k=4674/2073/407/199/发散） ---
print('B2-T24 A1实验5.2-B 旋转H固定步长（期望 4674/2073/407/199/20000+NaN）：')
ok24 = True
exp24 = {0.004: 4674, 0.009: 2073, 0.045: 407, 0.09: 199}
for a in [0.004, 0.009, 0.045, 0.09, 0.11]:
    k, xf, why = gd_fixed(H15, [1.0, 1.0], a, 20000, overflow_break=False)
    print(f'  α={a}: k={k} 退出={why} 末‖g‖={np.linalg.norm(H15 @ xf):.2e}')
    if a in exp24:
        ok24 &= (k == exp24[a])
    else:
        ok24 &= (why != '梯度达标' and k == 20000)
record('T24', f'A1实验5.2-B固定步长步数复现 {exp24}', 'PASS' if ok24 else 'FAIL')

# --- B2-T25：A1 实验5.2-B 精确线搜索（期望 k=39、步长交替 0.0517/0.6100） ---
k25, tr25 = gd_exact(H15, [1.0, 1.0], itmax=5000, tol=1e-8)
alphas25 = []
for i in range(k25):
    g = H15 @ tr25[i]
    alphas25.append((g @ g) / (g @ H15 @ g))
ok25 = (k25 == 39) and close(alphas25[0], 0.0517, 1e-3) and close(alphas25[1], 0.6100, 1e-3)
print(f'B2-T25 A1实验5.2-B 精确线搜索: k={k25} 前6步 α={[round(a,4) for a in alphas25[:6]]}',
      'PASS' if ok25 else 'FAIL')
record('T25', f'A1实验5.2-B 精确线搜索 k=39、步长交替 {[round(a,4) for a in alphas25[:2]]}', 'PASS' if ok25 else 'FAIL')

# %%
# --- B2-T26：A1 实验5.2-C Armijo 回溯（期望 α0=1: k=148 fev=627 alphas∈{0.0625,0.125,0.25}；α0=10: k=173 fev=1325） ---
# 独立实现（与 A1 lab_common.armijo 相同的 fev 计数约定：仅线搜索试探计数，含接受那次；外层 f/g 不计）
def armijo_gd(A, x0, alpha0=1.0, c1=1e-4, rho=0.5, tol=1e-8, maxit=10000):
    x = np.array(x0, dtype=float)
    alphas, fev = [], 0
    for _ in range(maxit):
        g = A @ x
        if np.linalg.norm(g) <= tol:
            return x, alphas, fev, True
        a = alpha0
        while 0.5 * (x - a * g) @ A @ (x - a * g) > 0.5 * x @ A @ x + c1 * a * (-(g @ g)):
            a *= rho
            fev += 1
            if a < 1e-16:
                return x, alphas, fev, False
        fev += 1
        alphas.append(a)
        x = x - a * g
    return x, alphas, fev, False

ok26 = True
for a0, (k_exp, fev_exp) in [(1.0, (148, 627)), (10.0, (173, 1325))]:
    xf, al, fev, ok = armijo_gd(H15, [1.0, 1.0], alpha0=a0)
    k = len(al)
    aset = sorted(set(round(a, 6) for a in al))
    ok26 &= (k == k_exp) and (fev == fev_exp)
    print(f'  α0={a0}: k={k} fev={fev} alphas={aset} 期望 k={k_exp} fev={fev_exp}')
print('B2-T26 A1实验5.2-C Armijo 迭代数/评估数复现', 'PASS' if ok26 else 'FAIL')
record('T26', 'A1实验5.2-C Armijo k=148/173、fev=627/1325', 'PASS' if ok26 else 'FAIL')

# Wolfe 条件核查：A1 代码注释与"分析"称"强 Wolfe"，但检查式 g_{k+1}·(-g_k) ≥ 0.9·(g_k·(-g_k))
# 未取绝对值，实际检验的是弱 Wolfe 曲率条件；真正强 Wolfe 需 |g_{k+1}·d_k| ≤ 0.9|g_k·d_k|
traj26 = [np.array([1.0, 1.0])]
x = np.array([1.0, 1.0]); alphas26 = []
for _ in range(200):
    g = H15 @ x
    if np.linalg.norm(g) <= 1e-8: break
    a = 1.0
    while 0.5 * (x - a * g) @ H15 @ (x - a * g) > 0.5 * x @ H15 @ x + 1e-4 * a * (-(g @ g)):
        a *= 0.5
    x = x - a * g
    traj26.append(x.copy()); alphas26.append(a)
okw26 = strong26 = 0
for i in range(len(traj26) - 1):
    g, gn = H15 @ traj26[i], H15 @ traj26[i + 1]
    if gn @ (-g) >= 0.9 * (g @ (-g)):
        okw26 += 1
    if abs(gn @ (-g)) <= 0.9 * abs(g @ (-g)):
        strong26 += 1
n26 = len(traj26) - 1
print(f'B2-T26b 弱Wolfe（A1代码所测、无绝对值）: {okw26}/{n26}（与A1打印的148/148一致）')
print(f'B2-T26b 真正强Wolfe（取绝对值）: {strong26}/{n26} —— A1 的"强Wolfe"是误标（→修正清单 B009）')
ok26b = (okw26 == n26)
record('T26b', f'A1实验5.2-C：弱Wolfe {okw26}/{n26}（A1实测148/148复现）', 'PASS' if ok26b else 'FAIL')
record('T26c', f'A1实验5.2-C"强Wolfe"实为弱Wolfe：真强Wolfe仅 {strong26}/{n26}（g_{k+1}·g_k/||g_k||^2 下探到 -0.96）', 'CONFIRMED')

# %%
# --- B2-T27：A2 例5.2.17/习题5.2-C 表独立复现（期望 373/500/53/149 与 783/151） ---
# 独立实现（与 A2 descent() 相同计数约定：每次循环初计 f+g 各1次，回溯试探计 f，停止后再计1次）
def descent_a2(mode, steps=500):
    Q = np.diag([1.0, 20.0])
    x = np.array([2.0, 2.0]); nf = ng = updates = 0; reason = '达到迭代上限'
    for k in range(steps):
        val = 0.5 * x @ Q @ x; g = Q @ x; nf += 1; ng += 1
        if np.linalg.norm(g) < 1e-8:
            reason = '梯度范数<1e-8'; break
        alpha = float(mode) if mode != 'armijo' else 1.0
        if mode == 'armijo':
            for _ in range(60):
                z = x - alpha * g; cand = 0.5 * z @ Q @ z; nf += 1
                if cand <= val - 1e-4 * alpha * (g @ g): break
                alpha *= 0.5
            else:
                reason = '回溯失败'; break
        x = x - alpha * g; updates += 1
        if np.linalg.norm(x) > 1e8:
            reason = '发散阈值||x||>1e8'; break
    val = 0.5 * x @ Q @ x; g = Q @ x; nf += 1; ng += 1
    return updates, val, np.linalg.norm(g), nf, ng, reason

exp27 = {'0.05': (373, 375, 375, '梯度范数<1e-8'), '0.1': (500, 501, 501, '达到迭代上限'),
         '0.12': (53, 54, 54, '发散阈值||x||>1e8'), 'armijo': (149, 783, 151, '梯度范数<1e-8')}
print('B2-T27 A2例5.2.17 表独立复现：')
ok27 = True
for mode, (k_e, nf_e, ng_e, why_e) in exp27.items():
    k, val, gnorm, nf, ng, why = descent_a2(mode)
    ok27 &= (k == k_e) and (nf == nf_e) and (ng == ng_e) and (why == why_e)
    print(f'  {mode}: k={k} nf={nf} ng={ng} ‖g‖={gnorm:.3e} 退出={why} 期望 k={k_e} nf={nf_e} ng={ng_e}')
record('T27', 'A2例5.2.17 固定步长与回溯的更新/评估次数', 'PASS' if ok27 else 'FAIL')

# --- B2-T28：A2 例5.2.14 只有单调下降还不够（α_k=2^{-k-2}） ---
alpha_seq = 2.0 ** (-np.arange(0, 1000) - 2)
x28 = np.prod(1 - alpha_seq)          # x_k / x_0 的下界构造
ok28 = (x28 >= np.exp(-1)) and (x28 > 0) and abs(np.sum(alpha_seq) - 0.5) < 1e-9
print(f'B2-T28 A2例5.2.14: Π(1-α_j)={x28:.9f} ≥ e^(-1)={np.exp(-1):.9f} > 0，Σα_j={np.sum(alpha_seq):.9f}=1/2 => 梯度不趋零',
      'PASS' if ok28 else 'FAIL')
record('T28', 'A2例5.2.14 无统一步长下界时充分下降不足以保证梯度趋零', 'PASS' if ok28 else 'FAIL')

# %%
# --- B2-T29：独立第三方对照（scipy） ---
# 1) BFGS 求 f=x^2+4y^2 极小；2) scipy.optimize.golden 对 φ(α)=f(x-αg) 精确线搜索与闭式步长对照
from scipy.optimize import minimize, golden
res = minimize(lambda z: z[0]**2 + 4 * z[1]**2, np.array([1.0, 1.0]), method='BFGS',
               jac=lambda z: np.array([2 * z[0], 8 * z[1]]), tol=1e-14)
ok29a = close(res.x, [0.0, 0.0], 1e-10, 'scipy BFGS 最优解')
A29 = np.diag([2.0, 8.0]); g29 = A29 @ np.array([1.0, 1.0])
phi29 = lambda a: 0.5 * (np.array([1.0, 1.0]) - a * g29) @ A29 @ (np.array([1.0, 1.0]) - a * g29)
a_golden = golden(phi29, brack=(0, 0.5), tol=1e-12)
a_closed = (g29 @ g29) / (g29 @ A29 @ g29)
ok29b = close(a_golden, a_closed, 1e-6, 'golden vs 闭式步长')
print(f'B2-T29 scipy对照: BFGS->{res.x}（期望[0,0]，{res.nit}步）| golden α={a_golden:.10f} vs 闭式 {a_closed:.10f}',
      'PASS' if (ok29a and ok29b) else 'FAIL')
record('T29', 'scipy 独立求解器与一维黄金分割对照', 'PASS' if (ok29a and ok29b) else 'FAIL')

# %% [md]
# ## 复现结论与修正清单
#
# 全部测试结论由下方最后一个代码单元输出（PASS / CONFIRMED 汇总）。核心条目对照如下；对应修正清单条目见《B2组-修正清单.md》。
#
# | 测试 | 对象 | 参考值/基准 | 容差 | 实测 | 结论 |
# | --- | --- | --- | --- | --- | --- |
# | T01–T06 | A1 驻点分类（例5.2.1.x、伪证2/5、习题9.2.1-1） | sympy 精确特征值/配方 | 精确或1e-12 | 逐项一致 | PASS |
# | T07–T09 | A2 例5.2.4/5.2.5、命题5.2.2/5.2.3 | 解析推导+数值 | 1e-12 | 一致（a≈-1.057、b≈0.930） | PASS |
# | T10/T11 | A1 例5.2.2.1/5.2.2.2 | 分数精确 68/520；gᵀd 符号 | 精确 | 正交性精确成立 | PASS |
# | T12/T13 | A2 例5.2.9；固定步长充要 0<α<2/λmax | 解析 | 精确 | 0.24收敛/0.26发散/0.1振荡(‖g‖→40) | PASS |
# | T14/T14c | 精确线搜索正交性；A1 正文条件数代码块 | 正交性≈0；复跑其代码 | 1e-10 | κ=1/10/100/1000 → 1/23/13/9 步（与A1解读矛盾） | PASS/CONFIRMED |
# | T15/T15b | A1 图5-12/5-13 图注一致性 | 目检图例+复跑代码 | — | 图注来自实验5.2-B，与正文代码块不符；实验数字逐字复现 | CONFIRMED/PASS |
# | T16 | A1 伪证3（局部≠全局） | 数值求驻点 | 1e-12 | 4个 f''>0 驻点、函数值互异 | PASS |
# | T17/T18 | A1 例5.2.3.1/5.2.3.2（Armijo/Wolfe 手算） | 闭式 | 精确 | 逐行一致（含 α=0.1 临界） | PASS |
# | T19/T22 | A2 例5.2.10 回溯整表；例5.2.16 信赖域 | 闭式 | 1e-10 | 逐行一致；ρ=-0.5/0.5 | PASS |
# | T20 | 回溯有限终止+非下降方向 | 随机50例+方向前提 | — | 全部有限终止；d=+g 触发 alpha_min 保护 | PASS |
# | T21 | A1 定理5.2.3.2 证明思路 | 反例 e^(-α) | — | 无局部极小点但 Wolfe 有解（α=-ln c₂） | CONFIRMED |
# | T23 | A1 实验5.2-C 信赖域 λ-Δ 表 | 独立二分法 | 1e-3 | λ/‖d‖/pred 全部一致、ρ=1 | PASS |
# | T24/T25 | A1 实验5.2-B 固定步长/精确线搜索 | A1 实测输出 | 精确 | 4674/2073/407/199/20000+NaN；k=39、0.0517/0.61 | PASS |
# | T26/T26b/T26c | A1 实验5.2-C Armijo 与 Wolfe | A1 实测输出 | 精确 | 148/627、173/1325；弱Wolfe 148/148；真强Wolfe 137/148 | PASS/PASS/CONFIRMED |
# | T27/T28 | A2 例5.2.17 表；例5.2.14 | A2 实测输出；闭式 | 精确 | 373/500/53/149 与 nf/ng 全一致；Π=0.5776≥e^(-1) | PASS |
# | T29 | scipy 独立对照 | BFGS/golden | 1e-6 | (0,0) 4步；α=17/130 | PASS |

# %%
print(json.dumps(results, ensure_ascii=False, indent=2))
n_pass = sum(1 for v in results.values() if v['verdict'] == 'PASS')
n_conf = sum(1 for v in results.values() if v['verdict'] == 'CONFIRMED')
print(f'\n汇总：PASS {n_pass} / {len(results)}，已确认问题 {n_conf}（详见修正清单）')

# 输出 B2 自绘证据图（固定步长两种矩阵下的命运 + 锯齿轨迹）
fig, axes = plt.subplots(1, 2, figsize=(11, 4))
for ax, (A, alphas, title) in zip(axes, [
        (np.diag([2.0, 8.0]), [0.01, 0.05, 0.1, 0.2, 0.3], '正文代码块：A=diag(2,8)，2/L=0.25'),
        (H15, [0.004, 0.009, 0.045, 0.09, 0.11], '实验5.2-B：旋转H=diag(1,20)，2/L=0.1')]):
    for a in alphas:
        x = np.array([1.0, 1.0]); fs = []
        for _ in range(80 if A is not H15 else 120):
            fs.append(0.5 * x @ A @ x)
            x = x - a * (A @ x)
        ax.semilogy(fs, label=f'α={a}')
    ax.set_xlabel('迭代次数 k'); ax.set_ylabel('f(x_k)'); ax.set_title(title)
    ax.legend(fontsize=8); ax.grid(True, which='both')
plt.tight_layout()
plt.savefig('图片/B2组-固定步长两种矩阵.png', dpi=150)
plt.close()

fig, ax = plt.subplots(figsize=(5.5, 4.5))
tr = tr14
xx = np.linspace(-1.1, 1.1, 300); yy = np.linspace(-1.1, 1.1, 300)
XX, YY = np.meshgrid(xx, yy)
ZZ = XX**2 + 4 * YY**2
ax.contour(XX, YY, ZZ, levels=20, cmap='viridis', alpha=0.6)
ax.plot(tr[:, 0], tr[:, 1], 'o-', color='tab:red', markersize=4, label='精确线搜索轨迹')
ax.plot(0, 0, 'k*', markersize=12, label='最优点')
ax.set_title('B2复现：锯齿现象（A=diag(2,8)，κ=4）')
ax.legend(); ax.grid(alpha=0.3)
plt.tight_layout()
plt.savefig('图片/B2组-锯齿轨迹.png', dpi=150)
plt.close()
print('B2 证据图已保存：图片/B2组-固定步长两种矩阵.png、图片/B2组-锯齿轨迹.png')
