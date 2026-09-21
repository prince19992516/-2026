# 环境文件怎么用

初学者请先阅读[从零安装教程](../教程/01-环境安装与运行.md)。在课程根目录运行 `.\course.cmd setup`（Windows）或 `python3.12 course.py setup`（macOS/Linux），助手会读取这里的主依赖配置。不要在本目录里直接启动课程助手。

| 文件 | 用途 | 初次使用是否需要手动操作 |
| --- | --- | --- |
| requirements.txt | Python 3.12 CPU教学环境的固定直接依赖 | 不需要，setup自动安装 |
| requirements-ai.txt | PyTorch/JAX等训练扩展 | 不需要，扩展实验时按进阶教程安装 |
| environment.yml | Conda替代配置 | 不需要，已选择Conda时才使用 |
| Dockerfile | 容器替代配置 | 不需要，助教或熟悉Docker的同学使用 |

不用同时安装三套环境。[进阶说明](../教程/06-进阶环境与原始命令.md)包含Conda、Docker的完整窗口安排和不使用助手时的原始命令。首次安装完成后，平时只需lab、check，不必每天重装。

主环境直接依赖固定版本；间接依赖仍需在正式验收时记录实际安装结果。可选AI组合做过Windows依赖解析，未代替实际训练和GPU验证。
