# 03 GitHub协作与提交

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
git switch -c chapter-01-a-g22
```

分支名示例中01是章节，a是本章角色，g22是实际学生小组编号；这三部分按[章节分工表](../协作管理/章节分工表.md)修改。B/C角色分别用b/c；每次新任务从更新后的main建立新分支。

## 修改、亲自运行、保存与提交

只修改本组当前角色负责的文件。下面以G22在第一章承担A角色为例。同一章节同一角色有两个小组，先约定各自负责的小节或文件，再分支提交；报告与AI对话按小组编号分段，保留彼此的记录，不覆盖另一组的内容。

1. 在JupyterLab中完成文字和代码修改。
2. 点击 **Kernel → Restart Kernel and Run All Cells**，等待全部单元结束。
3. 逐项核对输出是否符合公式、参考值和适用条件，记录实际结果；有报错或差异就如实分析，不删除问题凑结论。
4. 按 **Ctrl+S** 保存Notebook，保存对应报告。
5. 在课程根目录新开窗口B，逐行执行下列Git命令，每次回车后等待完成：

```bash
git status
git add 教材/第01章-误差的代价/A组-实验.ipynb 教材/第01章-误差的代价/A组-编写报告.md
git diff --cached --stat
git commit -m "第01章 A组：补充误差实验与编写报告"
git push -u origin chapter-01-a-g22
```

上面只暂存两个示范文件；本次修改了正文、习题等文件时逐个加入。不要把 `.venv`、密钥、运行缓存和无关资料一并上传。

公开的分工表、报告与AI对话记录只填写小组编号，不填写学生姓名、GitHub账号或私人联系方式；含成员信息的原始Excel不上传。Git提交身份会出现在版本记录中，可使用昵称和GitHub的noreply邮箱。

成功时commit输出本次版本编号和修改摘要，push显示分支已上传；浏览器可能提示登录GitHub，请使用自己的账号。出现权限错误则先确认邀请是否接受，或采用下方Fork流程。`nothing to commit`通常表示没有已保存的新改动，或忘了git add；先看git status，不要反复提交空版本。

在GitHub仓库打开 **Pull requests → New pull request**，base选main，compare选自己的分支。填写PR模板和报告链接，说明亲自运行的步骤、实际输出及未解决问题，按审阅意见继续在同一分支提交即可。合并通常由助教负责。

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
git switch -c chapter-02-b-g22
```

Fork用户使用upstream更新main。例子中G22从第01章的A角色换到第02章的B角色，再在第03章完成C角色；分支名按实际章节、角色和小组编号填写。

D/E整合组不用套用ABC轮换示例。按[整合任务](../协作管理/章节分工表.md)在更新后的main上建立如`integrate-ch01-04-d1-g2`的分支，提交实际整合的文件；PR说明整合范围、解决的问题和仍需A/B/C处理的事项。生成整本网页的步骤见[生成与查看教材](05-生成与查看教材.md)。
