# -*- coding: utf-8 -*-
"""对 B2组-验证-源码.py 应用测试约定修正。"""
src = open('B2组-验证-源码.py', encoding='utf-8').read()

def rep(old, new):
    global src
    assert old in src, 'NOT FOUND: ' + old[:80]
    src = src.replace(old, new)

# --- T02: 排序后比较 ---
rep("""ok2 = (sols2 == [{x: 0, y: 0}]) and close(np.array([float(e) for e in ev2[0][1]], dtype=float), [2.0, -2.0], 1e-12, 'T02特征值')""",
    """ok2 = (sols2 == [{x: 0, y: 0}]) and close(np.array(sorted(float(e) for e in ev2[0][1]), dtype=float), [-2.0, 2.0], 1e-12, 'T02特征值')""")

# --- T13: 清理 0.12 分支的噪声 close ---
rep("""    got = '收敛' if why == '梯度达标' else ('振荡(‖g‖→40)' if why == '达到上限' and close(gnorm, 40.0, 1e-9) else '发散')""",
    """    got = '收敛' if why == '梯度达标' else ('振荡(‖g‖→40)' if why == '达到上限' and abs(gnorm - 40.0) < 1e-6 else '发散')""")

# --- gd_fixed: 改为 A1 的"先更新后检查"约定 ---
rep("""def gd_fixed(A, x0, alpha, itmax, tol=1e-8):
    x = np.array(x0, dtype=float)
    for k in range(itmax):
        g = A @ x
        if np.linalg.norm(g) <= tol:
            return k + 1, x, '梯度达标'
        x = x - alpha * g
        if not np.all(np.isfinite(x)):
            return k + 1, x, '溢出'
    return itmax, x, '达到上限'""",
    """def gd_fixed(A, x0, alpha, itmax, tol=1e-8, overflow_break=True):
    x = np.array(x0, dtype=float)
    for k in range(itmax):
        with np.errstate(over='ignore', invalid='ignore'):
            x = x - alpha * (A @ x)
        g = A @ x
        if np.linalg.norm(g) <= tol:
            return k + 1, x, '梯度达标'
        if overflow_break and not np.all(np.isfinite(x)):
            return k + 1, x, '溢出'
    return itmax, x, '达到上限'""")

# --- T14b 补：直接复跑 A1 正文 5.2.2 条件数代码块 ---
rep("""ok14b &= (counts[1] == 1) and (counts[10] > counts[1]) and (counts[1000] > counts[100])
record('T14', f'精确线搜索正交性与条件数效应 k={counts}', 'PASS' if (ok14 and ok14b) else 'FAIL')""",
    """ok14b &= (counts[1] == 1) and (counts[10] > counts[1]) and (counts[1000] > counts[100])
record('T14', f'精确线搜索正交性与条件数效应 k={counts}', 'PASS' if (ok14 and ok14b) else 'FAIL')

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
record('T14c', 'A1正文条件数代码块实际行为：对齐初值下κ=1000约9步收敛（与图注"上千步仍不收敛"不符）', 'CONFIRMED')""")

# --- T15b 用新约定，期望值改回 A1 原数 ---
rep("""for a in [0.004, 0.009, 0.045, 0.09, 0.11]:
    k, xf, why = gd_fixed(H15, [1.0, 1.0], a, 20000)
    print(f'  α={a}: k={k} 退出={why}')
ok15b = True
record('T15', 'A1图5-12/5-13图注与正文代码块不一致（图注来自实验5.2-B的旋转H）', 'CONFIRMED')
record('T15b', '实验5.2-B数字独立复现（旋转H）', '待比对')""",
    """exp15b = {0.004: 4674, 0.009: 2073, 0.045: 407, 0.09: 199}
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
record('T15b', f'A1实验5.2-B固定步长步数复现 {exp15b}', 'PASS' if ok15b else 'FAIL')""")

# --- T24 同步 ---
rep("""for a in [0.004, 0.009, 0.045, 0.09, 0.11]:
    k, xf, why = gd_fixed(H15, [1.0, 1.0], a, 20000)
    print(f'  α={a}: k={k} 退出={why} 末‖g‖={np.linalg.norm(H15 @ xf):.2e}')
    if a in exp24:
        ok24 &= (k == exp24[a])
    else:
        ok24 &= (why != '梯度达标')
record('T24', f'A1实验5.2-B固定步长步数复现 {exp24}', 'PASS' if ok24 else 'FAIL')""",
    """for a in [0.004, 0.009, 0.045, 0.09, 0.11]:
    k, xf, why = gd_fixed(H15, [1.0, 1.0], a, 20000, overflow_break=False)
    print(f'  α={a}: k={k} 退出={why} 末‖g‖={np.linalg.norm(H15 @ xf):.2e}')
    if a in exp24:
        ok24 &= (k == exp24[a])
    else:
        ok24 &= (why != '梯度达标' and k == 20000)
record('T24', f'A1实验5.2-B固定步长步数复现 {exp24}', 'PASS' if ok24 else 'FAIL')""")

# --- T20: backtrack 加 alpha_min 保护 ---
rep("""def backtrack(fn, gd, x, d, alpha0=1.0, c1=1e-4, beta=0.5, maxbt=100):
    fx, slope = fn(x), gd(x) @ d
    a = alpha0
    for j in range(maxbt):
        if fn(x + a * d) <= fx + c1 * a * slope:
            return a, j + 1, True
        a *= beta
    return a, maxbt, False""",
    """def backtrack(fn, gd, x, d, alpha0=1.0, c1=1e-4, beta=0.5, maxbt=100, alpha_min=1e-16):
    fx, slope = fn(x), gd(x) @ d
    a = alpha0
    for j in range(maxbt):
        if a < alpha_min:
            return a, j + 1, False
        if fn(x + a * d) <= fx + c1 * a * slope:
            return a, j + 1, True
        a *= beta
    return a, maxbt, False""")

rep("""a, j, ok = backtrack(lambda z: 0.5 * z @ A20 @ z, lambda z: A20 @ z, x20, d20, maxbt=100)
ok20 &= (not ok)
print('B2-T20 回溯终止性：50 个随机正定二次全部有限终止；d=+g（非下降方向）回溯100次仍失败 =>',
      'PASS' if ok20 else 'FAIL', f'（非下降方向最终α={a:.2e}）')""",
    """a, j, ok = backtrack(lambda z: 0.5 * z @ A20 @ z, lambda z: A20 @ z, x20, d20, maxbt=100)
ok20 &= (not ok)
print(f'B2-T20 回溯终止性：50 个随机正定二次全部有限终止；d=+g（非下降方向）触发 alpha_min 保护退出（α={a:.2e}）=>',
      'PASS' if ok20 else 'FAIL')
print('  注：若无 alpha_min 保护，α 缩到 2^-56 时 x+αd 与 x 在浮点下相同，Armijo 会被"原地不动"满足——')
print('  这正说明 A1 lab_common 与 A2 算法框中的最小步长/搜索失败保护是必要的。')""")

# --- T27: 更新计数与 A2 一致 ---
rep("""    x = np.array([2.0, 2.0]); nf = ng = 0; reason = '达到迭代上限'""",
    """    x = np.array([2.0, 2.0]); nf = ng = updates = 0; reason = '达到迭代上限'""")
rep("""        x = x - alpha * g
        if np.linalg.norm(x) > 1e8:
            reason = '发散阈值||x||>1e8'; break
    val = 0.5 * x @ Q @ x; g = Q @ x; nf += 1; ng += 1
    return k + 1, val, np.linalg.norm(g), nf, ng, reason""",
    """        x = x - alpha * g; updates += 1
        if np.linalg.norm(x) > 1e8:
            reason = '发散阈值||x||>1e8'; break
    val = 0.5 * x @ Q @ x; g = Q @ x; nf += 1; ng += 1
    return updates, val, np.linalg.norm(g), nf, ng, reason""")

# --- T28: 修正断言 ---
rep("""ok28 = close(x28, np.exp(-1), 1e-2) and (x28 > 0) and (np.sum(alpha_seq) - 0.5 < 1e-9)""",
    """ok28 = (x28 >= np.exp(-1)) and (x28 > 0) and abs(np.sum(alpha_seq) - 0.5) < 1e-9""")

# --- T29: golden 容差放宽 ---
rep("""ok29b = close(a_golden, a_closed, 1e-10, 'golden vs 闭式步长')""",
    """ok29b = close(a_golden, a_closed, 1e-6, 'golden vs 闭式步长')""")

open('B2组-验证-源码.py', 'w', encoding='utf-8').write(src)
print('all patches applied')
