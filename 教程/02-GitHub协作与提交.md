# 02 GitHub协作与提交

## 第一次准备
先完成[环境安装与首次运行](01-环境安装与运行.md)，注册GitHub账号。以下Git命令在**课程根目录的空闲终端窗口B**输入；运行JupyterLab的窗口A保持打开。新建分支、更新文件前先保存并关闭相关Notebook标签页，避免浏览器把旧版本重新保存到磁盘。

“保存Notebook”只保存到本机；“commit”建立本地版本记录；“push”上传到GitHub；“PR”申请将你的分支合并到课程main。四件事不同。下面代码块中的命令逐行执行，每行回车，确认成功再下一行；不要连接成一行。

在仓库根目录配置自己的提交身份（姓名和邮箱替换成自己的，不要照抄示例）：

先确认自己已经接受助教的协作者邀请；没有邀请的同学先看下面“没有仓库写权限”，配置自己的Fork后再继续。GitHub用户名、提交姓名、邮箱是不同字段：用户名用于登录和邀请，提交姓名用于版本记录。提交邮箱可在GitHub个人 **Settings → Emails** 查看；若使用GitHub提供的隐私邮箱，完整复制其noreply地址。

```bash
git config user.name "你的姓名或昵称"
git config user.email "你的GitHub提交邮箱"
git switch main
git pull --ff-only origin main
git switch -c chapter-01-a-g01
```

分支名示例中01是章节，a是本章角色，g01是实际学生小组编号；这三部分按实际任务修改。B/C角色分别用b/c；每次新任务从更新后的main建立新分支。

## 修改、检查、提交

只修改本组负责的文件。下面以A组第一章为例。先在JupyterLab保存文件；回到窗口B，Windows运行：

```powershell
.\course.cmd check 教材/第01章-误差的代价
```

macOS/Linux运行：

```bash
python3.12 course.py check 教材/第01章-误差的代价
```

选择自己系统的命令，等检查完成且无失败后，再输入以下Git命令，每次一行。指定章节时结构和陷阱格式仍查全仓库，Notebook只运行指定章节：

```bash
git status
git add 教材/第01章-误差的代价/实验.ipynb 教材/第01章-误差的代价/编写报告.md
git diff --cached --stat
git commit -m "第01章 A组：补充误差实验与编写报告"
git push -u origin chapter-01-a-g01
```

上面只暂存两个示范文件；本次修改了正文、习题等文件时逐个加入。不要把 `.venv`、密钥、运行缓存和无关资料一并上传。

成功时commit输出本次版本编号和修改摘要，push显示分支已上传；浏览器可能提示登录GitHub，请使用自己的账号。出现权限错误则先确认邀请是否接受，或采用下方Fork流程。`nothing to commit`通常表示没有已保存的新改动，或忘了git add；先看git status，不要反复提交空版本。

在GitHub仓库打开 **Pull requests → New pull request**，base选main，compare选自己的分支。填写PR模板和报告链接，查看Actions结果，按审阅意见继续在同一分支提交即可。合并通常由助教负责。

打开Actions里对应PR的运行记录：绿色为通过，红色为失败，黄色/转圈为正在运行。失败时点击具体步骤查看第一条错误，修复后重新commit和push；不要用上一份提交的绿灯说明当前版本通过。

## 没有仓库写权限

Fork是把课程仓库复制到自己的GitHub账号下，之后向自己的副本上传，再申请合并到课程仓库。

1. 登录GitHub，打开课程仓库，点击右上角 **Fork**，在创建页面确认Owner是自己，点击 **Create fork**。
2. 创建后，页面左上角的所有者应是你的用户名；点击绿色 **Code → HTTPS**，复制自己的仓库地址。
3. 如果已经按安装教程clone了课程仓库，**保留现有文件和环境**。在课程根目录运行 `git remote -v`，检查origin目前指向哪里；然后将下行地址替换为刚复制的个人Fork地址，执行：

```bash
git remote set-url origin https://github.com/你的GitHub用户名/-2026.git
```

4. 再运行 `git remote -v`，确认origin的所有者已是自己。这只是改变上传地址，不会删除本机修改。如果尚未下载文件，直接按安装教程clone自己的Fork地址即可。
5. 将课程仓库设为upstream（用于取得老师更新）。以下add只在首次配置时执行；如果提示upstream已存在，先用 `git remote -v` 核对地址，不重复添加。工作区干净时依次运行：

```bash
git remote add upstream https://github.com/prince19992516/-2026.git
git fetch upstream
git switch main
git merge --ff-only upstream/main
```

之后回到上文的新建分支、修改、检查和提交流程，向自己的origin执行push。浏览器进入自己的Fork，选择 **Contribute → Open pull request**，或在课程仓库的New pull request中选择 **compare across forks**。目标仓库选`prince19992516/-2026`、base选`main`，来源选自己的Fork与作业分支；核对修改后点击 **Create pull request**，等待助教审阅。

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
git switch -c chapter-02-b-g01
```

Fork用户使用upstream更新main。例子中G01从第01章的A角色换到第02章的B角色，之后还需在另一个章节完成C角色；分支名按实际章节、角色和小组编号填写。
