# 第01章《误差的代价》C2 AI 对话记录

G19 · 首轮 · 2026-11-21 · 工具为 Codex（GPT-6，界面未提供细分模型标识）

## 1　查找分工和提交要求

提问原文：

> 直接看github [https://github.com/prince19992516/-2026/tree/main](https://github.com/prince19992516/-2026/tree/main)
>
> 我是G19组现在要做一下第一章的C2组工作，你帮我做一下，你参看一下这个分工要求，提交内容要求什么的

Codex 回复摘录：

> 已确认 G19 是第一章《误差的代价》的 C2，需要交五份材料。

判断依据为第一章 README 的分工、C 组操作指南和该章模板。审阅 A1、A2、B1、B2 各自版本，提交文件沿用课程规定的 C2 组前缀。[第一章 README](https://github.com/prince19992516/-2026/blob/286ce25e5f6f17fba579abe07f21fcf23eb59e7d/教材/第01章-误差的代价/README.md)

## 2　独立检查条件数和交叉熵

向 Codex 子任务提出的复核请求原文如下。本机临时路径已隐去。

> Read-only independent review of Chapter 1 A1 G20 updates sections 1.3–1.4, compare with B evidence and possible D3 carryovers. Source [本机临时路径] at latest GitHub main (checkout finishing). Send exact located, verified high-impact findings and most useful comparison. No files.

AI 回答摘录：

> It divides by rounded root residual for g(t)=t²−2 using inconsistent input scales. Intended map f(a)=sqrt(a), a=2: κ=|a/(2sqrt(a))/sqrt(a)|=1/2

采用条件数线索。重新运行 D3 第 7 格，并由被开方数到平方根的解析映射复算，差异和改法记录为 CH01-G19-C003。其他审查分别比较了 A1、A2 与 B1 的交叉熵运算顺序。对高分目标的微小损失和大公共偏移这两个例子，采用 80 位 Decimal 独立核对，再用新启动的 Jupyter 内核保存实际输出。候选结论须由推导和数值共同支持。

## 3　代码来源与人工核验状态

- Codex 在 2026-11-21 查阅 GitHub 实际文件和提交，编写 C2 最小验证代码，运行原稿及 C2 Notebook。固定输入、参考值、误差容差和输出可逐格复查。
- 运行和文档检查属于 Codex 执行记录。G19 组员已确认复核本轮交件。本轮未发生的六组讨论、A/B 修订和新版本复测按待办记录。
- B1 公开记录的 DeepSeek 线索属于外组材料。它不提供原始完整回复，按已披露的转述使用，详见 [AI 陷阱记录](C2组-AI陷阱.md)。

[手动推导](C2组-手动推导.md) · [人工复核](C2组-人工复核.ipynb) · [批判报告](C2组-批判报告.md)
