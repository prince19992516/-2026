# 02 GitHub协作与提交

## 第一次准备
先完成[环境安装与首次运行](01-环境安装与运行.md)，注册GitHub账号。以下Git命令在**课程根目录的空闲终端窗口B**输入；运行JupyterLab的窗口A保持打开。新建分支、更新文件前先保存并关闭相关Notebook标签页，避免浏览器把旧版本重新保存到磁盘。

“保存Notebook”只保存到本机；“commit”建立本地版本记录；“push”上传到GitHub；“PR”申请将你的分支合并到课程main。四件事不同。下面代码块中的命令逐行执行，每行回车，确认成功再下一行；不要连接成一行。

在仓库根目录配置自己的提交身份（姓名和邮箱替换成自己的，不要照抄示例）：

```bash
git config user.name "你的姓名或昵称"
git config user.email "你的GitHub提交邮箱"
git switch main
git pull --ff-only origin main
git switch -c chapter-01-a-yourname
```

分支名示例中01是章节，a是组别。B/C分别用b/c；每次新任务从更新后的main建立新分支。

## 修改、检查、提交

只修改本组负责的文件。下面以A组第一章为例。先在JupyterLab保存文件；回到窗口B，Windows运行：

```powershell
.\course.cmd check 教材/第01章-误差
```

macOS/Linux运行：

```bash
python3.12 course.py check 教材/第01章-误差
```

选择自己系统的命令，等检查完成且无失败后，再输入以下Git命令，每次一行。指定章节时结构和陷阱格式仍查全仓库，Notebook只运行指定章节：

```bash
git status
git add 教材/第01章-误差/实验.ipynb 教材/第01章-误差/编写报告.md
git diff --cached --stat
git commit -m "第01章 A组：补充误差实验与编写报告"
git push -u origin chapter-01-a-yourname
```

上面只暂存两个示范文件；本次修改了正文、习题等文件时逐个加入。不要把 `.venv`、密钥、运行缓存和无关资料一并上传。

成功时commit输出本次版本编号和修改摘要，push显示分支已上传；浏览器可能提示登录GitHub，请使用自己的账号。出现权限错误则先确认邀请是否接受，或采用下方Fork流程。`nothing to commit`通常表示没有已保存的新改动，或忘了git add；先看git status，不要反复提交空版本。

在GitHub仓库打开 **Pull requests → New pull request**，base选main，compare选自己的分支。填写PR模板和报告链接，查看Actions结果，按审阅意见继续在同一分支提交即可。合并通常由助教负责。

打开Actions里对应PR的运行记录：绿色为通过，红色为失败，黄色/转圈为正在运行。失败时点击具体步骤查看第一条错误，修复后重新commit和push；不要用上一份提交的绿灯说明当前版本通过。

## 没有仓库写权限

在GitHub上Fork仓库，克隆自己的Fork；向自己的origin推送分支，再向课程仓库main发PR。将课程仓库设为upstream，以后从upstream更新：

```bash
git remote add upstream https://github.com/prince19992516/-2026.git
git fetch upstream
git switch main
git merge --ff-only upstream/main
```

如果本地main有个人提交导致快进失败，先把工作保存到分支，再请助教协助整理；不要使用强推覆盖课程历史。GitHub HTTPS认证使用凭据管理器或令牌，不使用账号密码作为Git密码。

## B/C如何固定被审版本

```bash
git rev-parse HEAD
```

在报告填写该完整SHA。查看某份A组PR时，先获取其分支，再以其实际commit为准。需要保持当前工作目录时，使用独立worktree检查某个版本：

```bash
git worktree add --detach ../course-review 完整commitSHA
```

把“完整commitSHA”替换为真实值，不要照抄。B组审A的版本，C组同时记录A的内容版本与B的报告/验证代码版本。A修复后新建复测条目，不能只悄悄修改旧SHA。

## Notebook冲突

Notebook是JSON文件，不宜盲目编辑冲突标记。先保留双方备份，确定本次基准版本，在Jupyter逐个移入需要保留的单元；检查公式、代码和输出，再重启内核运行全部。若不确定，请助教共同处理，不能直接丢弃他组证据。

## 合并后开始下一任务

```bash
git switch main
git pull --ff-only origin main
git switch -c chapter-02-a-yourname
```

Fork用户使用upstream更新main。分支名按实际章节和组别填写。
