# 05 补装Python库与记录依赖（选读）

先完成[环境安装与首次运行](01-环境安装与运行.md)。本教程用于后续实验需要额外库的情况，普通起步实验使用入门教程中的依赖即可。

## 1. 确认安装到哪个Python

在课程根目录的空闲终端输入：

Windows：

```powershell
.\.venv\Scripts\python.exe -c "import sys; print(sys.executable)"
```

macOS/Linux：

```bash
.venv/bin/python -c "import sys; print(sys.executable)"
```

输出应是当前课程目录下.venv中的Python。后面的安装命令使用同一个Python路径，无需手动激活环境。

## 2. 补装一个库

先阅读实验说明，明确库名和版本；不要直接照抄AI建议的一大串未知库。例如要补装本课程用到的SymPy 1.13.3：

Windows：

```powershell
.\.venv\Scripts\python.exe -m pip install sympy==1.13.3
```

macOS/Linux：

```bash
.venv/bin/python -m pip install sympy==1.13.3
```

已满足该版本时会显示Requirement already satisfied。安装完成后，回到Notebook重启内核，再运行代码。库的用途、安装版本及所用命令写进本章报告，以便B组在新环境复现。

**在什么地方安装：** 原工作副本的实验缺库，就在原课程根目录安装；B/C复现副本缺库，就先判断是否属于A已声明的依赖，再在那个副本的根目录操作。两份`.venv`互不通用。安装到原目录不会给复现目录自动补齐。

**补装后的具体操作：** 等终端提示符回来且没有ERROR，回浏览器点击 **Kernel → Restart Kernel and Run All Cells**，从头运行；仅按一次Shift+Enter可能仍使用旧内核中已加载的库。若仍提示No module named，先在Notebook运行`import sys; print(sys.executable)`，确认当前内核路径属于刚安装的环境，再判断包名是否正确。

**报告中至少写这些：** 库的用途、系统、CPU/GPU、完整安装命令、实际安装版本、使用它的Notebook与单元、运行结果。AI建议安装多个库时，先确认本实验是否真的使用；不要为了消除一个报错随意升级所有依赖。

第六章的完整神经网络训练由学生扩展；若选用PyTorch、JAX或GPU，由A组根据实际算法和设备查阅对应框架官方安装说明，写明所需版本、设备和操作。入门阶段不必先装全部训练框架。

## 3. 记录实际安装的版本

在空闲终端输入以下命令，结果会打印在终端：

Windows：

```powershell
.\.venv\Scripts\python.exe -m pip freeze
```

macOS/Linux：

```bash
.venv/bin/python -m pip freeze
```

把与实验有关的版本记录在报告中。需要保存完整文本时，可在命令末尾加 `> 本机依赖快照.txt`；同名文件会被覆盖，所以保留旧证据时请换文件名。提交前阅读内容，去掉私人路径或敏感地址。

## 4. 课程助手和原始命令的关系

课程助手用于环境安装完成之后，只有三个功能：

| 助手命令 | 做什么 | 终端是否持续占用 |
| --- | --- | --- |
| lab | 启动本课程.venv里的JupyterLab | 是，Ctrl+C停止 |
| build | 由course.py生成HTML | 否，完成后返回 |
| preview | 在本机8000端口提供教材网页 | 是，Ctrl+C停止 |

Windows可双击course.cmd，菜单1启动、2生成、3预览、0退出。直接启动Jupyter也可在根目录输入 `.\.venv\Scripts\python.exe -m jupyterlab`；Mac/Linux对应 `.venv/bin/python -m jupyterlab`。生成教材的命令见[生成与查看教材](04-生成与查看教材.md)。

本课程的教材配置使用Jupyter Book 1.x；安装时按入门教程中的版本操作。调整依赖前先保存工作，记录变更原因，再由B组亲自复现。
