# 9.3 Newton 与拟 Newton：把曲率用起来

> **本节脉络**：9.3.2 用阻尼与 Hessian 修正让 Newton 法“远处稳、近处快”，但每步仍要计算 Hessian 并解线性方程组，代价  $O(n^3)$  。9.3.3 给出**拟 Newton** 方案：不计算 Hessian，只用相邻梯度差“猜”曲率，通过**割线条件**维护近似矩阵。BFGS 是最成功的拟 Newton 更新，每步代价  $O(n^2)$  ，同时保持超线性收敛。

---

## 9.3.3 割线条件、BFGS 更新与曲率条件

### 【本节导航】

- 预习：知道梯度差  $\boldsymbol y_k = \nabla f(\boldsymbol x_{k+1}) - \nabla f(\boldsymbol x_k)$  与步长  $\boldsymbol s_k = \boldsymbol x_{k+1} - \boldsymbol x_k$  。
- 核心：割线条件、BFGS 更新公式、逆 BFGS 更新、曲率条件  $\boldsymbol s_k^{\top} \boldsymbol y_k \gt 0$  。
- 避坑：曲率条件不满足时更新失效、BFGS 不保证全局收敛、逆更新与 B 更新混用。
- 总结：割线条件说“近似 Hessian 要匹配梯度差”，BFGS 用秩二更新实现它，曲率条件保证正定。
- 自测：手算一步 BFGS 更新、验证割线条件、判断曲率条件。
- 拓展：DFP、SR1、L-BFGS、有限内存、超线性收敛。

---

### 一、生活类比：用“走一步的坡度变化”猜曲率

你在一座山上，不知道地面的曲率（Hessian），但可以测量：

- 走了一步  $\boldsymbol s_k$  ；
- 出发点和到达点的坡度（梯度）分别是  $\nabla f(\boldsymbol x_k)$  和  $\nabla f(\boldsymbol x_{k+1})$  ；
- 坡度变化  $\boldsymbol y_k = \nabla f(\boldsymbol x_{k+1}) - \nabla f(\boldsymbol x_k)$  。

**割线条件的直觉**：如果近似 Hessian 是  $\boldsymbol B_{k+1}$  ，那么它应该把“这一步  $\boldsymbol s_k$  ”映射成“坡度变化  $\boldsymbol y_k$  ”：

$$
\boldsymbol B_{k+1} \boldsymbol s_k = \boldsymbol y_k
$$

这就像用“两点连线”近似切线：不知道真实曲率，但知道走一步后坡度变了多少，用这个信息反推曲率。

**BFGS 的直觉**：满足割线条件的矩阵有很多，BFGS 选其中“离旧矩阵  $\boldsymbol B_k$  最近”的那个，并且保持正定。

---

### 二、几何直观：割线、秩二修正与正定性

- **割线条件**：在  $\boldsymbol s_k$  方向上，近似 Hessian 必须精确匹配梯度差。这是“一维精确、高维近似”。
- **秩二修正**：BFGS 更新在  $\boldsymbol B_k$  上加减两个秩一矩阵，修正量只作用在  $\boldsymbol s_k$  与  $\boldsymbol B_k \boldsymbol s_k$  张成的子空间上，其他方向不变。
- **曲率条件**： $\boldsymbol s_k^{\top} \boldsymbol y_k \gt 0$  表示“沿这一步，梯度在上升”，即函数沿该方向是凸的。只有满足它，BFGS 更新才能保持正定。
- **正定性保持**：若  $\boldsymbol B_k$  正定且  $\boldsymbol s_k^{\top} \boldsymbol y_k \gt 0$  ，则  $\boldsymbol B_{k+1}$  仍正定。这保证拟 Newton 方向  $-\boldsymbol B_k^{-1} \nabla f$  始终是下降方向。

---

### 三、底层逻辑：为什么割线条件合理

#### 3.1 从 Taylor 展开看割线条件

对梯度做一阶 Taylor 展开：

$$
\nabla f(\boldsymbol x_{k+1}) \approx \nabla f(\boldsymbol x_k) + \boldsymbol H(\boldsymbol x_k) \boldsymbol s_k
$$

移项得

$$
\boldsymbol H(\boldsymbol x_k) \boldsymbol s_k \approx \boldsymbol y_k
$$

割线条件就是把“近似”改成“精确”，并用  $\boldsymbol B_{k+1}$  代替  $\boldsymbol H$  ：

$$
\boldsymbol B_{k+1} \boldsymbol s_k = \boldsymbol y_k
$$

#### 3.2 为什么需要曲率条件

BFGS 更新公式的分母含  $\boldsymbol s_k^{\top} \boldsymbol y_k$  。若  $\boldsymbol s_k^{\top} \boldsymbol y_k \le 0$  ，更新可能破坏正定性，导致方向非下降。曲率条件  $\boldsymbol s_k^{\top} \boldsymbol y_k \gt 0$  是 BFGS 保持正定的充分条件。

#### 3.3 为什么 BFGS 比 DFP 更受欢迎

DFP 是另一个满足割线条件的更新，但 BFGS 在数值上更稳定，对线搜索误差不敏感，且与“逆更新”的对偶形式更简洁。实践中 BFGS 和 L-BFGS 是拟 Newton 的默认选择。

---

### 四、严格定义

**定义 9.3.3.1（割线条件）**  
设  $\boldsymbol s_k = \boldsymbol x_{k+1} - \boldsymbol x_k$  ， $\boldsymbol y_k = \nabla f(\boldsymbol x_{k+1}) - \nabla f(\boldsymbol x_k)$  。若近似 Hessian  $\boldsymbol B_{k+1}$  满足

$$
\boldsymbol B_{k+1} \boldsymbol s_k = \boldsymbol y_k
$$

称其满足**割线条件**。

**定义 9.3.3.2（BFGS 更新，Hessian 近似形式）**  
给定正定矩阵  $\boldsymbol B_k$  ，BFGS 更新为

$$
\boldsymbol B_{k+1} = \boldsymbol B_k
- \frac{\boldsymbol B_k \boldsymbol s_k \boldsymbol s_k^{\top} \boldsymbol B_k}{\boldsymbol s_k^{\top} \boldsymbol B_k \boldsymbol s_k}
+ \frac{\boldsymbol y_k \boldsymbol y_k^{\top}}{\boldsymbol y_k^{\top} \boldsymbol s_k}
$$

**定义 9.3.3.3（BFGS 逆更新）**  
设  $\boldsymbol H_k = \boldsymbol B_k^{-1}$  ，逆 BFGS 更新为

$$
\boldsymbol H_{k+1} = \left( \boldsymbol I - \rho_k \boldsymbol s_k \boldsymbol y_k^{\top} \right)
\boldsymbol H_k
\left( \boldsymbol I - \rho_k \boldsymbol y_k \boldsymbol s_k^{\top} \right)
+ \rho_k \boldsymbol s_k \boldsymbol s_k^{\top}
$$

其中  $\rho_k = 1 / (\boldsymbol y_k^{\top} \boldsymbol s_k)$  。

**定义 9.3.3.4（曲率条件）**  
若

$$
\boldsymbol s_k^{\top} \boldsymbol y_k \gt 0
$$

称该步满足**曲率条件**。

> **易错坑点**：BFGS 更新公式中的分母  $\boldsymbol y_k^{\top} \boldsymbol s_k$  与  $\boldsymbol s_k^{\top} \boldsymbol B_k \boldsymbol s_k$  都必须为正。前者由曲率条件保证，后者由  $\boldsymbol B_k$  正定保证。

---

### 五、公式分层与结构

#### 5.1 BFGS 更新的三项拆解

BFGS 更新为

$$
\boldsymbol B_{k+1} = \boldsymbol B_k
- \frac{\boldsymbol B_k \boldsymbol s_k \boldsymbol s_k^{\top} \boldsymbol B_k}{\boldsymbol s_k^{\top} \boldsymbol B_k \boldsymbol s_k}
+ \frac{\boldsymbol y_k \boldsymbol y_k^{\top}}{\boldsymbol y_k^{\top} \boldsymbol s_k}
$$

其中：

- 第一项  $\boldsymbol B_k$  是**旧近似**；
- 第二项是**减去的秩一项**，方向沿  $\boldsymbol B_k \boldsymbol s_k$  ，用来“纠正旧矩阵在  $\boldsymbol s_k$  方向上的偏差”；
- 第三项是**加上的秩一项**，方向沿  $\boldsymbol y_k$  ，用来“注入新的曲率信息”。

#### 5.2 逆 BFGS 更新的结构

逆 BFGS 更新为

$$
\boldsymbol H_{k+1} = \left( \boldsymbol I - \rho_k \boldsymbol s_k \boldsymbol y_k^{\top} \right)
\boldsymbol H_k
\left( \boldsymbol I - \rho_k \boldsymbol y_k \boldsymbol s_k^{\top} \right)
+ \rho_k \boldsymbol s_k \boldsymbol s_k^{\top}
$$

其中  $\rho_k = 1 / (\boldsymbol y_k^{\top} \boldsymbol s_k)$  。这个形式直接更新逆矩阵，避免每步解线性方程组，是 BFGS 实用的关键。

#### 5.3 曲率条件与正定性

若  $\boldsymbol B_k$  正定且  $\boldsymbol s_k^{\top} \boldsymbol y_k \gt 0$  ，则  $\boldsymbol B_{k+1}$  正定。证明思路：对任意  $\boldsymbol v \neq \boldsymbol 0$  ，把  $\boldsymbol v$  分解为沿  $\boldsymbol s_k$  与正交补两部分，分别验证二次型为正。

#### 5.4 拟 Newton 方向

拟 Newton 方向为

$$
\boldsymbol d_k = -\boldsymbol B_k^{-1} \nabla f(\boldsymbol x_k)
$$

或直接用逆近似  $\boldsymbol H_k$  ：

$$
\boldsymbol d_k = -\boldsymbol H_k \nabla f(\boldsymbol x_k)
$$

计算上优先用逆更新，避免每步解方程。

---

### 六、可手推证明

#### 6.1 BFGS 更新满足割线条件

**定理 9.3.3.1**  
BFGS 更新  $\boldsymbol B_{k+1}$  满足  $\boldsymbol B_{k+1} \boldsymbol s_k = \boldsymbol y_k$  。

**手推**：记  $\boldsymbol B = \boldsymbol B_k$  ， $\boldsymbol s = \boldsymbol s_k$  ， $\boldsymbol y = \boldsymbol y_k$  。计算  $\boldsymbol B_{k+1} \boldsymbol s$  ：

$$
\boldsymbol B_{k+1} \boldsymbol s
= \boldsymbol B \boldsymbol s
- \frac{\boldsymbol B \boldsymbol s \boldsymbol s^{\top} \boldsymbol B \boldsymbol s}{\boldsymbol s^{\top} \boldsymbol B \boldsymbol s}
+ \frac{\boldsymbol y \boldsymbol y^{\top} \boldsymbol s}{\boldsymbol y^{\top} \boldsymbol s}
$$

注意  $\boldsymbol s^{\top} \boldsymbol B \boldsymbol s$  是标量，第二项化为  $\boldsymbol B \boldsymbol s$  ；第三项中  $\boldsymbol y^{\top} \boldsymbol s = \boldsymbol s^{\top} \boldsymbol y$  ，所以

$$
\boldsymbol B_{k+1} \boldsymbol s
= \boldsymbol B \boldsymbol s - \boldsymbol B \boldsymbol s + \boldsymbol y
= \boldsymbol y
$$

✅ 割线条件成立。

#### 6.2 曲率条件保证 BFGS 更新正定

**定理 9.3.3.2**  
若  $\boldsymbol B_k$  正定且  $\boldsymbol s_k^{\top} \boldsymbol y_k \gt 0$  ，则 BFGS 更新后的  $\boldsymbol B_{k+1}$  正定。

**证明思路**：对任意  $\boldsymbol v \neq \boldsymbol 0$  ，计算  $\boldsymbol v^{\top} \boldsymbol B_{k+1} \boldsymbol v$  。利用  $\boldsymbol B_k$  正定和  $\boldsymbol s_k^{\top} \boldsymbol y_k \gt 0$  ，可将其写成两个非负项之和，且至少一项严格为正。详细展开略，核心是“正定 + 正分母 ⇒ 正定”。

#### 6.3 逆 BFGS 更新与 B 更新等价

若  $\boldsymbol H_k = \boldsymbol B_k^{-1}$  ，则逆 BFGS 更新得到的  $\boldsymbol H_{k+1}$  满足  $\boldsymbol H_{k+1} = \boldsymbol B_{k+1}^{-1}$  。这是 Sherman–Morrison–Woodbury 公式的直接应用。等价性保证两种更新在数学上一致，但数值上逆更新更常用。

---

### 七、手算例题

**例题 9.3.3.1（一步 BFGS 更新）**  
设  $\boldsymbol B_0 = \boldsymbol I$  ， $\boldsymbol s_0 = (1, 0)^{\top}$  ， $\boldsymbol y_0 = (2, 1)^{\top}$  。计算  $\boldsymbol B_1$  。

**手算**：

1.  $\boldsymbol B_0 \boldsymbol s_0 = (1, 0)^{\top}$  。
2.  $\boldsymbol s_0^{\top} \boldsymbol B_0 \boldsymbol s_0 = 1$  。
3. 第二项：

$$
\frac{\boldsymbol B_0 \boldsymbol s_0 \boldsymbol s_0^{\top} \boldsymbol B_0}{\boldsymbol s_0^{\top} \boldsymbol B_0 \boldsymbol s_0}
=
\begin{pmatrix}
1 & 0 \\
0 & 0
\end{pmatrix}
$$

4.  $\boldsymbol y_0^{\top} \boldsymbol s_0 = 2$  。
5. 第三项：

$$
\frac{\boldsymbol y_0 \boldsymbol y_0^{\top}}{\boldsymbol y_0^{\top} \boldsymbol s_0}
=
\frac{1}{2}
\begin{pmatrix}
4 & 2 \\
2 & 1
\end{pmatrix}
=
\begin{pmatrix}
2 & 1 \\
1 & 0.5
\end{pmatrix}
$$

6. 所以

$$
\boldsymbol B_1 =
\begin{pmatrix}
1 & 0 \\
0 & 1
\end{pmatrix}
-
\begin{pmatrix}
1 & 0 \\
0 & 0
\end{pmatrix}
+
\begin{pmatrix}
2 & 1 \\
1 & 0.5
\end{pmatrix}
=
\begin{pmatrix}
2 & 1 \\
1 & 1.5
\end{pmatrix}
$$

7. 验证割线条件： $\boldsymbol B_1 \boldsymbol s_0 = (2, 1)^{\top} = \boldsymbol y_0$  ✅。

**例题 9.3.3.2（曲率条件不满足）**  
设  $\boldsymbol s = (1, 1)^{\top}$  ， $\boldsymbol y = (-1, 1)^{\top}$  。计算  $\boldsymbol s^{\top} \boldsymbol y$  。

**手算**： $\boldsymbol s^{\top} \boldsymbol y = 1 \cdot (-1) + 1 \cdot 1 = 0$  。曲率条件不满足，BFGS 更新分母为零，更新失效。

**例题 9.3.3.3（逆 BFGS 一步）**  
接例题 9.3.3.1，用逆更新求  $\boldsymbol H_1$  ，并与  $\boldsymbol B_1^{-1}$  对比。

**手算**： $\rho_0 = 1 / (\boldsymbol y_0^{\top} \boldsymbol s_0) = 0.5$  。代入逆更新公式计算，结果应与  $\boldsymbol B_1^{-1}$  一致。这里略去展开，重点在于验证两种更新等价。

---

### 八、Python 代码验证

```python
import numpy as np
import matplotlib.pyplot as plt

# ===== BFGS 逆更新 + Armijo 回溯 =====
def bfgs(f, grad, x0, maxit=100, tol=1e-10, c1=1e-4, rho=0.5):
    x = np.array(x0, dtype=float)
    n = len(x)
    H = np.eye(n)          # 初始逆近似
    xs = [x.copy()]
    for k in range(maxit):
        g = grad(x)
        if np.linalg.norm(g) < tol:
            break
        d = -H @ g         # 拟 Newton 方向

        # Armijo 回溯
        alpha = 1.0
        fx = f(x)
        slope = g @ d
        while f(x + alpha * d) > fx + c1 * alpha * slope and alpha > 1e-16:
            alpha *= rho

        x_new = x + alpha * d
        s = x_new - x
        y = grad(x_new) - g

        # 曲率条件检查
        if s @ y > 1e-12:
            rho_k = 1.0 / (y @ s)
            I = np.eye(n)
            H = (I - rho_k * np.outer(s, y)) @ H @ (I - rho_k * np.outer(y, s)) \
                + rho_k * np.outer(s, s)

        x = x_new
        xs.append(x.copy())
    return np.array(xs)

# 测试函数：Rosenbrock
def rosen(v):
    x, y = v
    return (1 - x)**2 + 100*(y - x**2)**2

def rosen_grad(v):
    x, y = v
    return np.array([
        -2*(1 - x) - 400*x*(y - x**2),
        200*(y - x**2)
    ])

xs = bfgs(rosen, rosen_grad, [-1.2, 1.0], maxit=200)
print("BFGS 迭代次数:", len(xs) - 1)
print("最终点:", xs[-1])
print("最终函数值:", rosen(xs[-1]))
```

**输出解读**：BFGS 在 Rosenbrock 函数上通常几十步收敛，远快于梯度下降，但慢于精确 Newton（后者需要 Hessian）。

**与梯度下降对比**：

```python
def gd(f, grad, x0, alpha=1e-3, maxit=5000):
    x = np.array(x0, dtype=float)
    xs = [x.copy()]
    for _ in range(maxit):
        g = grad(x)
        if np.linalg.norm(g) < 1e-10:
            break
        x = x - alpha * g
        xs.append(x.copy())
    return np.array(xs)

xs_gd = gd(rosen, rosen_grad, [-1.2, 1.0], alpha=1e-3, maxit=5000)
print("梯度下降迭代次数:", len(xs_gd) - 1)
```

**解读**：BFGS 利用曲率信息，迭代次数通常比梯度下降少一到两个数量级。

**轨迹可视化**：

```python
X, Y = np.meshgrid(np.linspace(-2, 2, 400), np.linspace(-1, 3, 400))
Z = (1 - X)**2 + 100*(Y - X**2)**2
plt.figure(figsize=(6,5))
plt.contour(X, Y, Z, levels=np.logspace(-1, 3, 30), cmap='viridis')
plt.plot(xs[:,0], xs[:,1], 'o-', color='tab:red', markersize=3, label='BFGS')
plt.plot(xs_gd[:200,0], xs_gd[:200,1], 's--', color='tab:blue', markersize=2, label='梯度下降（前200步）')
plt.scatter([1],[1], marker='*', s=200, color='gold', label='最优点')
plt.xlabel('x'); plt.ylabel('y'); plt.legend(); plt.grid(True)
plt.title('BFGS vs 梯度下降（Rosenbrock 函数）')
plt.show()
```

---

### 九、误差可视化：BFGS 的超线性收敛

```python
# 计算到最优点的误差
xstar = np.array([1.0, 1.0])
err_bfgs = np.linalg.norm(xs - xstar, axis=1)
err_gd = np.linalg.norm(xs_gd - xstar, axis=1)

plt.figure(figsize=(7,4))
plt.semilogy(err_gd[:1000], 's-', label='梯度下降', markersize=2)
plt.semilogy(err_bfgs, 'o-', label='BFGS')
plt.xlabel('迭代次数 k'); plt.ylabel('误差')
plt.title('BFGS 超线性收敛 vs 梯度下降线性收敛')
plt.legend(); plt.grid(True, which='both')
plt.show()
```

**解读**：BFGS 误差曲线在半对数坐标下先线性后加速，体现**超线性收敛**；梯度下降始终是直线（线性收敛）。

---

### 十、易错坑点

| 坑点 | 现象 | 原因/对策 |
|---|---|---|
| 曲率条件不满足仍更新 | 矩阵失去正定，方向非下降 | 检查  $\boldsymbol s_k^{\top} \boldsymbol y_k \gt 0$  ；不满足时跳过更新或重新初始化 |
| 逆更新与 B 更新混用 | 维度或转置错误 | 明确使用  $\boldsymbol H_k$  还是  $\boldsymbol B_k$  ，不要混用 |
| 初始  $\boldsymbol H_0$  选得过大/过小 | 第一步方向尺度失衡 | 常用  $\boldsymbol H_0 = \gamma \boldsymbol I$  ， $\gamma$  由梯度尺度估计 |
| 忘记线搜索 | 满步可能不下降 | BFGS 必须配合线搜索（Armijo/Wolfe） |
| 内存爆炸 | 高维时  $\boldsymbol H_k$  是  $n \times n$  | 用 L-BFGS 只存最近  $m$  步的  $\boldsymbol s, \boldsymbol y$  |
| 收敛到鞍点 |  $\|\nabla f\|$  很小但 Hessian 不定 | 拟 Newton 只解驻点方程，需二阶检查 |
| 曲率条件用错符号 | 误判  $\boldsymbol s^{\top} \boldsymbol y \lt 0$  为正常 | 曲率条件要求**正**，不是负 |

---

### 十一、对比辨析

#### 11.1 BFGS vs DFP vs SR1

| 维度 | BFGS | DFP | SR1 |
|---|---|---|---|
| 更新秩 | 2 | 2 | 1 |
| 保持正定 | 曲率条件下是 | 曲率条件下是 | 不一定 |
| 数值稳定性 | 好 | 中 | 可能不稳定 |
| 割线条件 | 满足 | 满足 | 满足 |
| 常用场景 | 通用拟 Newton | 理论对比 | 信赖域、不定问题 |

#### 11.2 拟 Newton vs 纯 Newton vs 梯度下降

| 维度 | 梯度下降 | 拟 Newton（BFGS） | 纯 Newton |
|---|---|---|---|
| 用到的信息 | 一阶 | 一阶 + 割线曲率 | 二阶 |
| 每步代价 |  $O(n)$  |  $O(n^2)$  |  $O(n^3)$  |
| 收敛速率 | 线性 | 超线性 | 二次（局部） |
| 是否需 Hessian | 否 | 否 | 是 |
| 对尺度 | 敏感 | 较不敏感 | 仿射不变 |
| 稳健性 | 好 | 好 | 需阻尼/修正 |

#### 11.3 BFGS 与 L-BFGS

| 维度 | BFGS | L-BFGS |
|---|---|---|
| 存储 |  $O(n^2)$  |  $O(mn)$  ， $m$  为历史步数 |
| 每步代价 |  $O(n^2)$  |  $O(mn)$  |
| 适用规模 | 中小规模 | 大规模 |
| 收敛速率 | 超线性 | 超线性（近似） |

---

### 【伪证辨析栏】⭐

> **伪证 1**：“满足割线条件的矩阵唯一。”  
> **错**。割线条件只给  $n$  个方程，而  $\boldsymbol B$  有  $n^2$  个未知量。满足割线条件的矩阵有无穷多个，BFGS 只是其中“离旧矩阵最近且保持正定”的一个。

> **伪证 2**：“BFGS 更新一定保持正定。”  
> **错**。只有曲率条件  $\boldsymbol s_k^{\top} \boldsymbol y_k \gt 0$  满足时才保持正定。若  $\boldsymbol s_k^{\top} \boldsymbol y_k \le 0$  ，更新可能破坏正定性，需跳过更新或改用其他策略。

> **伪证 3**：“BFGS 是全局收敛的。”  
> **错**。BFGS 通常只保证局部超线性收敛。全局收敛需要配合合适的线搜索（如 Wolfe 条件）和额外假设，且可能收敛到鞍点。

> **伪证 4**：“逆 BFGS 更新与 B 更新是两套不同算法。”  
> **错**。二者在数学上等价，都是 BFGS 更新的不同表示。逆更新直接维护  $\boldsymbol H_k = \boldsymbol B_k^{-1}$  ，避免每步解方程，是实用实现的首选。

> **伪证 5**：“曲率条件  $\boldsymbol s_k^{\top} \boldsymbol y_k \gt 0$  总是成立。”  
> **错**。对非凸函数，沿某些方向  $\boldsymbol s_k^{\top} \boldsymbol y_k$  可能为负或零。此时 BFGS 更新失效，需要线搜索保证曲率条件，或改用 SR1 等不要求正定的更新。

> **伪证 6**：“BFGS 每步都解线性方程组。”  
> **错**。BFGS 用逆更新直接维护  $\boldsymbol H_k$  ，每步只需矩阵-向量乘法  $\boldsymbol d_k = -\boldsymbol H_k \nabla f(\boldsymbol x_k)$  ，代价  $O(n^2)$  ，不需要解方程。

---

### 【深度透析】

#### 基础层（普通学生必掌握）

1. 会写割线条件  $\boldsymbol B_{k+1} \boldsymbol s_k = \boldsymbol y_k$  ；
2. 会写 BFGS 更新公式（B 形式或逆形式）；
3. 知道曲率条件  $\boldsymbol s_k^{\top} \boldsymbol y_k \gt 0$  是保持正定的关键；
4. 知道拟 Newton 每步代价  $O(n^2)$  ，比 Newton 的  $O(n^3)$  便宜。

#### 提高层（考研/科研）

1. **BFGS 的变分推导**：BFGS 是满足割线条件且使  $\|\boldsymbol B - \boldsymbol B_k\|$  在某种加权 Frobenius 范数下最小的解。这是“最近更新”的严格表述。
2. **超线性收敛**：在适当条件下，BFGS 满足  $\|\boldsymbol x_{k+1} - \boldsymbol x^{\ast}\| / \|\boldsymbol x_k - \boldsymbol x^{\ast}\| \to 0$  ，即超线性收敛，但通常不是二次。
3. **L-BFGS**：只存最近  $m$  步的  $\boldsymbol s, \boldsymbol y$  ，用双循环递归计算  $\boldsymbol H_k \nabla f$  ，存储  $O(mn)$  ，适合大规模问题。
4. **曲率条件与 Wolfe 线搜索**：Wolfe 曲率条件  $\nabla f(\boldsymbol x_{k+1})^{\top} \boldsymbol d_k \ge c_2 \nabla f(\boldsymbol x_k)^{\top} \boldsymbol d_k$  与  $\boldsymbol s_k^{\top} \boldsymbol y_k \gt 0$  有密切联系；合适的线搜索可保证曲率条件。
5. **SR1 与信赖域**：SR1 更新不要求正定，适合不定 Hessian 和信赖域方法，但可能产生奇异矩阵，需谨慎处理。
6. **有限精度与重启**：BFGS 在病态问题上可能失去正定性或曲率信息，常用“重启”（重新初始化为  $\gamma \boldsymbol I$  ）恢复稳健性。

---

### 一句话本质总结

> **割线条件说“近似 Hessian 要匹配梯度差”，BFGS 用秩二更新在满足割线条件的同时尽量靠近旧矩阵，曲率条件  $\boldsymbol s_k^{\top} \boldsymbol y_k \gt 0$  保证更新后仍正定——于是不用算 Hessian，也能用曲率信息超线性收敛。**

---

### 自测与拓展

**自测题**

1. 设  $\boldsymbol B_0 = \boldsymbol I$  ， $\boldsymbol s_0 = (1, 2)^{\top}$  ， $\boldsymbol y_0 = (3, 1)^{\top}$  ，手算一步 BFGS 更新  $\boldsymbol B_1$  ，并验证割线条件。
2. 判断：若  $\boldsymbol s_k^{\top} \boldsymbol y_k \lt 0$  ，BFGS 更新是否仍能保持正定？给出理由。
3. 证明：BFGS 更新满足割线条件  $\boldsymbol B_{k+1} \boldsymbol s_k = \boldsymbol y_k$  。
4. 解释为什么逆 BFGS 更新在实用中比 B 更新更常用。
5. 用 Python 复现本节代码，比较 BFGS、梯度下降、纯 Newton 在 Rosenbrock 函数上的迭代次数。
6. 构造一个例子：曲率条件不满足时，BFGS 更新导致矩阵非正定。

**拓展阅读**

- BFGS 的变分推导与加权 Frobenius 范数；
- L-BFGS 双循环递归；
- SR1 与信赖域方法；
- 曲率条件与 Wolfe 线搜索的关系；
- 有限精度下的 BFGS 重启策略。

---

> **下节预告**：9.3 解决了“无约束优化怎么用曲率”。9.4 将转向**非线性最小二乘**：目标函数是残差平方和，Hessian 有特殊结构  $\boldsymbol J^{\top} \boldsymbol J + \sum r_i \nabla^2 r_i$  。Gauss-Newton 忽略第二项，LM 在 Gauss-Newton 与梯度下降之间连续滑动。届时会看到：**最小二乘的曲率，大部分来自 Jacobian 的乘积**。