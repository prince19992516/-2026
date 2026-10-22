import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from pathlib import Path

# ===== 中文字体 =====
for font in ['SimHei', 'Microsoft YaHei', 'PingFang SC',
             'Noto Sans CJK SC', 'WenQuanYi Micro Hei']:
    mpl.rcParams['font.sans-serif'] = [font]
    mpl.rcParams['axes.unicode_minus'] = False
mpl.rcParams['figure.dpi'] = 150
mpl.rcParams['savefig.dpi'] = 150
mpl.rcParams['savefig.bbox'] = 'tight'

FIG_DIR = Path('../figures/ch09')
FIG_DIR.mkdir(parents=True, exist_ok=True)

def save(fig, name):
    path = FIG_DIR / name
    fig.savefig(path, bbox_inches='tight')
    print(f"saved: {path}")
    plt.close(fig)

# ========== 图 9.1.3-1 Newton 切线 ==========
fig, ax = plt.subplots(figsize=(7, 5))
f  = lambda x: x**3 - 2*x**2 + 0.5*x + 1
df = lambda x: 3*x**2 - 4*x + 0.5
xs = np.linspace(-0.2, 2.2, 400)
ax.plot(xs, f(xs), 'k-', lw=2, label=r'$f(x)$')
x_k = 1.8; y_k = f(x_k); slope = df(x_k)
x_next = x_k - y_k / slope
xt = np.linspace(x_k - 0.5, x_k + 0.8, 100)
ax.plot(xt, y_k + slope*(xt - x_k), 'r--', lw=1.5, label='切线')
ax.scatter([x_k], [y_k], color='tab:blue', s=80, zorder=5)
ax.annotate(r'$(x_k, f(x_k))$', (x_k, y_k),
            xytext=(x_k - 0.05, y_k + 0.6), fontsize=11)
ax.scatter([x_next], [0], color='tab:green', s=80, zorder=5)
ax.annotate(r'$x_{k+1}$', (x_next, 0),
            xytext=(x_next - 0.1, -0.5), fontsize=11)
ax.axhline(0, color='gray', lw=0.8)
ax.set_xlabel(r'$x$'); ax.set_ylabel(r'$f(x)$')
ax.set_title('Newton 法：用切线代替曲线')
ax.legend(loc='upper left'); ax.grid(True, alpha=0.3)
save(fig, 'fig-9.1.3-newton-tangent.png')

# ========== 图 9.1.3-2 三种方法收敛 ==========
fig, ax = plt.subplots(figsize=(7, 4))
def bisect_err(f, a, b, tol=1e-14, maxit=60):
    errs = []
    for _ in range(maxit):
        m = 0.5*(a+b); errs.append(abs(b-a)/2)
        if f(a)*f(m) < 0: b = m
        else: a = m
        if abs(b-a) < tol: break
    return np.array(errs)
def fp_err(g, x0, tol=1e-14, maxit=60):
    xs = [x0]; x = x0
    for _ in range(maxit):
        x = g(x); xs.append(x)
        if abs(xs[-1] - xs[-2]) < tol: break
    return np.abs(np.array(xs) - np.sqrt(2))
def newton_err(f, df, x0, tol=1e-14, maxit=60):
    xs = [x0]; x = x0
    for _ in range(maxit):
        x = x - f(x)/df(x); xs.append(x)
        if abs(xs[-1] - xs[-2]) < tol: break
    return np.abs(np.array(xs) - np.sqrt(2))
f  = lambda x: x**2 - 2
df = lambda x: 2*x
g  = lambda x: 0.5*(x + 2/x)
ax.semilogy(bisect_err(f, 0, 2), 's-', label='二分法（线性）')
ax.semilogy(fp_err(g, 1.0), 'd-', label='不动点迭代（线性）')
ax.semilogy(newton_err(f, df, 1.0), 'o-', label='Newton（二次）')
ax.set_xlabel('迭代次数 k'); ax.set_ylabel('误差')
ax.set_title('三种求根方法：Newton 二次收敛')
ax.legend(); ax.grid(True, which='both', alpha=0.3)
save(fig, 'fig-9.1.3-convergence.png')

# ========== 图 9.2.1-1 驻点三分图 ==========
fig, axes = plt.subplots(1, 3, figsize=(14, 4.2))
X, Y = np.meshgrid(np.linspace(-2, 2, 300), np.linspace(-2, 2, 300))
for ax, Z, title in zip(axes,
    [X**2 + Y**2, -(X**2 + Y**2), X**2 - Y**2],
    ['Hessian 正定 ⇒ 极小', 'Hessian 负定 ⇒ 极大', 'Hessian 不定 ⇒ 鞍点']):
    ax.contour(X, Y, Z, levels=15, cmap='viridis')
    ax.scatter([0], [0], color='gold', marker='*', s=200, zorder=5)
    ax.set_title(title); ax.set_xlabel('x'); ax.set_ylabel('y')
    ax.grid(True, alpha=0.3)
    ax.axhline(0, color='gray', lw=0.5); ax.axvline(0, color='gray', lw=0.5)
plt.tight_layout()
save(fig, 'fig-9.2.1-stationary-types.png')

# ========== 图 9.2.2-1 锯齿 ==========
fig, ax = plt.subplots(figsize=(7, 5))
A = np.array([[2.0, 0.0], [0.0, 8.0]]); b = np.zeros(2)
def gd_exact(x0, maxit=10):
    x = np.array(x0, dtype=float); xs = [x.copy()]
    for _ in range(maxit):
        g = A @ x - b
        if np.linalg.norm(g) < 1e-12: break
        alpha = (g @ g) / (g @ A @ g)
        x = x - alpha * g; xs.append(x.copy())
    return np.array(xs)
xs = gd_exact([1.0, 1.0])
X, Y = np.meshgrid(np.linspace(-0.3, 1.2, 300), np.linspace(-1.2, 1.2, 300))
Z = 0.5*(A[0,0]*X**2 + A[1,1]*Y**2)
ax.contour(X, Y, Z, levels=20, cmap='viridis')
ax.plot(xs[:,0], xs[:,1], 'o-', color='tab:red', lw=1.2,
        markersize=5, label='梯度下降轨迹')
ax.scatter([0],[0], marker='*', s=200, color='gold', label='最优点')
ax.set_xlabel('x'); ax.set_ylabel('y')
ax.set_title('精确线搜索的锯齿现象')
ax.legend(); ax.grid(True, alpha=0.3)
save(fig, 'fig-9.2.2-zigzag.png')

# ========== 图 9.2.2-2 固定步长 ==========
fig, ax = plt.subplots(figsize=(7, 4))
def gd_fixed(alpha, maxit=60):
    x = np.array([1.0, 1.0]); fs = []
    for _ in range(maxit):
        g = A @ x - b; fs.append(0.5 * x @ A @ x)
        x = x - alpha * g
        if np.linalg.norm(x) > 1e6:
            fs.append(np.nan); break
    return np.array(fs)
for alpha in [0.01, 0.1, 0.2, 0.3]:
    ax.semilogy(gd_fixed(alpha), 'o-', markersize=3, label=f'alpha={alpha}')
ax.set_xlabel('迭代次数 k'); ax.set_ylabel(r'$f(x_k)$')
ax.set_title('固定步长：太小慢，太大发散')
ax.legend(); ax.grid(True, which='both', alpha=0.3)
save(fig, 'fig-9.2.2-stepsize.png')

print("\n全部完成。请检查 ../figures/ch09/ 目录。")
