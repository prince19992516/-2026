# 第04章 矩阵的解剖 · 课后习题

## 题 1　4.1 直接法：LU与Cholesky

对矩阵 $A=\left(\begin{smallmatrix}0&1\\1&2\end{smallmatrix}\right)$ 做行交换后写出 $PA=LU$。取 $b=(1,3)^T$ 回代求解。这个矩阵能使用实 Cholesky 分解吗？

## 题 2　4.2 迭代法：CG与预条件

令 $A$ 为对角元正且相差若干数量级的对称正定矩阵。比较 CG 与 Jacobi 预条件 CG 的残差历史、构造成本和总时间，两者使用相同的初值与停止标准。

## 题 3　4.3 特征值与SVD

对 $A=\left(\begin{smallmatrix}1&1\\0&1\end{smallmatrix}\right)$ 计算特征值和奇异值。用一个秩一近似检验截断 SVD 的谱范数误差公式。

## 题 4　4.4 AI关联：可微求解器、PCA、LoRA

对 $64\times128$ 的权重矩阵，用秩至多为 4 的 LoRA 更新需要多少个因子参数？与中心化数据矩阵的秩四 PCA 重构比较，两者的矩阵、目标和可优化参数分别是什么？
