# 00 已经打开JupyterLab，接下来怎么办

你运行 `python -m jupyterlab` 后，浏览器打开JupyterLab，而原终端一直显示日志、不能继续输入命令：**这是正常运行，不是卡住。** JupyterLab是一个需要持续运行的服务。

## 推荐：保留窗口A，新开窗口B

| 位置 | 用来做什么 | 现在应该做什么 |
| --- | --- | --- |
| 窗口A：刚才启动Jupyter的终端 | 给浏览器里的JupyterLab提供服务 | 保持打开，不在日志后面粘贴新命令 |
| 浏览器里的JupyterLab | 写文字、公式、代码，运行Notebook | 保存你的文件 |
| 窗口B：新开的PowerShell终端 | 检查文件、运行测试、构建教材、Git提交 | 按下面步骤输入命令 |

### 1. 保存Notebook
在JupyterLab按 `Ctrl+S`，等待保存完成。检查脚本读取的是磁盘上的文件；未保存的修改不会被检查。检查期间先不要继续改同一份文件。

### 2. 新开PowerShell并进入课程文件夹
在Windows文件资源管理器里打开课程文件夹，即能看见 `README.md`、`course.cmd`、`教材`、`环境` 的那一层。点击顶部地址栏，输入 `powershell`，按回车。这就是窗口B。

**如果你当前的实际文件夹是 `C:\Users\prince\2026`**，也可以在新开的PowerShell逐行运行下面两条命令；其他学生应替换成自己的实际路径。

```powershell
cd "C:\Users\prince\2026"
```

```powershell
Get-Location
```

输出应是课程文件夹的路径。再输入 `dir`，应看到 `course.cmd` 和 `教材` 文件夹。路径有空格时保留双引号。

### 3. 先检查环境

```powershell
.\course.cmd doctor
```

看到“环境检查通过”再继续。如果提示没有课程环境，先输入下面这条安装命令，等待“安装完成”：

```powershell
.\course.cmd setup
```

如果原Jupyter用的是另一套Python，先保存并关闭原服务，再按[完整安装教程](01-环境安装与运行.md)从 `.\course.cmd lab` 重新打开，选择课程内核。

### 4. 检查教材

```powershell
.\course.cmd check
```

这条命令依次执行结构检查、AI陷阱格式检查、Notebook运行检查；中间失败会停止。结束后会回到 `PS ...>` 提示符。初始仓库预计显示9个passed、0个failed、16个placeholder。placeholder是学生尚未填写的B/C Notebook，不表示已经完成验证。

### 5. 需要整本教材时再构建

```powershell
.\course.cmd build
```

等到“构建完成”，再运行：

```powershell
.\course.cmd preview
```

浏览器打开 [本地教材](http://127.0.0.1:8000)。**preview也会持续占用窗口B**，这是正常现象。查看完，在窗口B按 `Ctrl+C` 停止；窗口A里的Jupyter可以继续保留。

## 只有一个终端窗口时
先保存文件，回到启动Jupyter的窗口按 `Ctrl+C`；如果出现 `Shutdown ... (y/[n])?`，输入 `y` 并回车。若第一次只是显示提示或没有退出，按终端提示操作，必要时再按一次 `Ctrl+C`。等重新出现 `PS ...>` 提示符后，才输入检查命令。此时浏览器里的Jupyter会断开，之后重新运行 `.\course.cmd lab` 即可。

关闭浏览器标签页不等于关闭Jupyter服务。不要为了获得命令行提示符反复重开Jupyter，也不要把后续命令粘贴进服务日志。

## 也可以用JupyterLab自带Terminal
点击左上角“+”，在Launcher里选择 **Terminal**。这是一个新的终端，不是Notebook代码单元。先确认所在目录；Windows默认PowerShell可运行 `Get-Location`，macOS/Linux运行 `pwd`。用 `cd` 进入课程根目录，再执行对应系统的助手命令。若打开的是cmd或其他shell，命令语法可能不同；初学者优先用上面的外部PowerShell方法。

macOS/Linux在新终端进入课程目录后，使用 `python3.12 course.py doctor`、`python3.12 course.py check`、`python3.12 course.py build`；启动服务与检查的窗口安排完全相同。

参考：[JupyterLab Terminal官方说明](https://jupyterlab.readthedocs.io/en/stable/user/terminal.html)；完整的首次安装、每日使用和报错处理见[环境安装教程](01-环境安装与运行.md)。
