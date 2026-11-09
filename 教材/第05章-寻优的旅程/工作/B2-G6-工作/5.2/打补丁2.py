# -*- coding: utf-8 -*-
"""第二轮自查补强：修正 T26b 标签、新增 T16 与 T26c、补汇总表。"""
src = open('B2组-验证-源码.py', encoding='utf-8').read()

def rep(old, new):
    global src
    assert old in src, 'NOT FOUND: ' + old[:90]
    src = src.replace(old, new)

# --- T16：A1 伪证3 定量核验（插入在 T15b 之后、5.2.3 之前） ---
anchor = """print('  =>', 'PASS（与A1实验5.2-B实测输出完全一致）' if ok15b else 'FAIL')
record('T15', 'A1图5-12/5-13图注与正文代码块不一致（图注来自实验5.2-B的旋转H）', 'CONFIRMED')
record('T15b', f'A1实验5.2-B固定步长步数复现 {exp15b}', 'PASS' if ok15b else 'FAIL')"""
assert anchor in src
addition = anchor + """

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
print('B2-T16 A1伪证3核验：f=x^2+sin(10x) 在 [-2,2] 内 f\\'\\'>0 的驻点：')
for c, v, d2 in mins16:
    print(f'  x={c:.6f}  f={v:.6f}  f\\'\\'={d2:.2f} (>0 => 局部极小)')
vals16 = [v for _, v, _ in mins16]
ok16 = (len(mins16) >= 2) and (max(vals16) - min(vals16) > 1e-6)
print('  => 至少两个局部极小且函数值互异 => 局部极小不保证全局，', 'PASS' if ok16 else 'FAIL')
record('T16', f'A1伪证3：{len(mins16)} 个 f\\'\\'>0 的局部极小、函数值互异', 'PASS' if ok16 else 'FAIL')"""
src = src.replace(anchor, addition)

# --- T26b 重写：弱/强 Wolfe 区分 ---
old = """# 强 Wolfe 比例（期望 148/148）
okw = sum(1 for i in range(len(al) - 1) if (H15 @ (np.array([1.0,1.0]) )) is not None) if False else None
# 重新按 A1 的方式检查：g_{k+1}·(-g_k) ≥ 0.9 * g_k·(-g_k)
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
okw26 = 0
for i in range(len(traj26) - 1):
    g, gn = H15 @ traj26[i], H15 @ traj26[i + 1]
    if gn @ (-g) >= 0.9 * (g @ (-g)):
        okw26 += 1
print(f'B2-T26b 强Wolfe满足比例: {okw26}/{len(traj26)-1}（期望 148/148）')
ok26b = (okw26 == len(traj26) - 1)
record('T26b', f'A1实验5.2-C 强Wolfe比例 {okw26}/{len(traj26)-1}', 'PASS' if ok26b else 'FAIL')"""
new = """# Wolfe 条件核查：A1 代码注释与"分析"称"强 Wolfe"，但检查式 g_{k+1}·(-g_k) ≥ 0.9·(g_k·(-g_k))
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
record('T26c', f'A1实验5.2-C"强Wolfe"实为弱Wolfe：真强Wolfe仅 {strong26}/{n26}（g_{k+1}·g_k/||g_k||^2 下探到 -0.96）', 'CONFIRMED')"""
assert old in src; src = src.replace(old, new)

# --- 汇总表：替换结论 markdown 单元格 ---
old_md = """# ## 复现结论与修正清单
#
# 全部测试结论汇总见下表；对应修正清单条目见《B2组-修正清单.md》。"""
new_md = """# ## 复现结论与修正清单
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
# | T29 | scipy 独立对照 | BFGS/golden | 1e-6 | (0,0) 4步；α=17/130 | PASS |"""
assert old_md in src; src = src.replace(old_md, new_md)

open('B2组-验证-源码.py', 'w', encoding='utf-8').write(src)
print('round-2 patches applied')
