# 第 02 章《逼近的智慧》B2 AI 对话记录

**G22 · 首轮 · 2026-11-11**

[验证报告](B2组-验证报告.md) · [验证 Notebook](B2组-验证.ipynb) · [修正清单](B2组-修正清单.md)

## 工具和分工

| 对象 | 已记录的工具或模型 | 用途 |
| --- | --- | --- |
| A1 · G8 | 公开记录使用 Codex 桌面和多 agent 工具，底层快照未披露。 | A1 稿及实验编写。 |
| A2 · G21 | 公开记录列出 Codex/GPT-6 和 DeepSeek 系列，精确快照未披露。 | A2 稿编写及分轮更新。 |
| B2 本轮 | Codex 协助设计参考、编写对照代码、实际重跑和整理。另用 Qwen2.5-0.5B-Instruct-GGUF Q4_K_M 本地 CPU 推理。 | Qwen 独立回答公开算例，依据解析式和实际运行判定其建议。 |

A1、A2 的完整被审版本列在验证报告。此记录的判断来自本轮程序与公式复核，组员解释与签认待补。[A1 AI 记录](https://github.com/prince19992516/-2026/blob/5d3ec4d66845131c1800654330ee9e3d0785e305/教材/第02章-逼近的智慧/工作/A1组-AI对话记录.md) · [A2 AI 记录](https://github.com/prince19992516/-2026/blob/a363a72c8f26d86cd6f129d3db0c3e63e2778729/教材/第02章-逼近的智慧/工作/A2组-AI对话记录.md)

## 2026-11-11 Codex 协作

**用户原话**

> 那你能帮我完成这四份文件吗？按照你说的步骤

**Codex 回复摘录**

> 我会先固定两份 A 稿的版本，写下独立参考值，再在新环境里重跑三份 Notebook。四份 B2 文件会记录实际输出、差异，以及需要你们签认或等 A 组修订后复测的事项。

实际执行先登记解析参考和容差，再清空原 Notebook 输出、在三套虚拟环境重跑。Qwen 的交叉核对在重跑期间准备，完成后用验证 Notebook 中的对照值逐项核验。三份 A 稿实验的实际单元计数、依赖与差异以验证报告为准。

## 2026-11-11 Qwen 交叉核对

模型为 Qwen2.5-0.5B-Instruct-GGUF Q4_K_M，模型修订 `9217f5db79a29953eb74d5343926648285ec7e67`，权重 SHA-256 `74a4da8c9fdbcd15bd1f6d01d621410d31c6fc00986f5eb687824e7b93d7a9db`。使用 `node-llama-cpp 3.22.3`，CPU 4 线程，每题独立上下文，温度 0、种子 2026、每题上限 420 个生成 token。系统提示原文为 `You are a numerical analysis checker. Answer in at most six lines with formulas and results. No external tools.`。以下是实际输出摘录，三条原回复均在生成上限附近截断。[模型卡与权重版本](https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct-GGUF/tree/9217f5db79a29953eb74d5343926648285ec7e67)

### 中心差分的表值和符号

**提问原文**

> For F(x)=sin(x^2)+exp(x), use D_h=(F(x+h)-F(x-h))/(2h). What is the sign of the leading coefficient of D_h-F'(x) in terms of F'''(x)? Give D_h at x=0.7 and h=0.1, or an unevaluated formula if you cannot calculate it.

**原回复摘录**

```text
   F'(x) = 2x \cos(x^2) + e^x
```

**后续回答摘录**

```text
   F''(x) = 2 \cos(x^2) + 4x^2 \sin(x^2) + e^x
```

**核验与取舍**　采纳一阶导式，舍弃二阶导式中的正号。链式法则给出 $F''=2\cos(x^2)-4x^2\sin(x^2)+e^x$。回复截至截断位置未给出请求的截断误差符号和数值。验证 Notebook §2.3 独立得到 $D_h-F'=h^2F'''/6+O(h^4)$，$D_{0.1}=3.241716680946303$，与 A2 原 Notebook 的首档结果吻合。对应 `CH02-G22-B004`。

### Simpson 单面板系数

**提问原文**

> One Simpson panel uses nodes u, u+h, u+2h. Is its factor h/3 or h/6 when the weights are 1,4,1? Show the exact result for f(x)=x^2 on [0,1] using both factors.

**原回复摘录**

```text
E_1 = \frac{b-2a}{36} \left[ f(x_0) + 4f(x_1) + 2f(x_2) + f(x_3) \right]
```

随后回复给出 `E_1 = \frac{7}{36}`。

**核验与取舍**　舍弃这段计算。题设的三个节点在 $[0,1]$ 上为 $0,1/2,1$，加权和为 $0+4(1/4)+1=2$。乘半宽系数 $h/3=1/6$ 得 $1/3$，乘 $h/6=1/12$ 得 $1/6$。解析积分和验证 Notebook §2.3 的实测一致。对应 `CH02-G22-B001`。

### 高频扰动与导数误差

**提问原文**

> For the function e_k(x)=sin(k*x)/k on [-1,1], with integer k>=2, find the sup norms of e_k and its first two derivatives. Give a point for each maximum.

**原回复摘录**

```text
\[ e_k'(x) = \frac{d}{dx} \left( \frac{\sin(kx)}{k} \right) = \frac{k \cos(kx)}{k} = \cos(kx) \]
```

```text
\[ e_k''(x) = \frac{d}{dx} \left( \cos(kx) \right) = -k \sin(kx) \]
```

**核验与取舍**　保留两条导数式，分别代入见证点完成检验。在 $k\ge2$ 时，$x=\pi/(2k)$ 属于 $[-1,1]$，在该点函数与二阶导的绝对值分别为 $1/k$、$k$。一阶导在 $x=0$ 取绝对值 1。正余弦的幅值上界说明三项均为上确界。验证 Notebook §2.4 实际检查了 $k=10,100,1000$。
