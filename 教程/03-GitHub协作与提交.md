# 03 GitHub协作与提交：把本机文件交到课程仓库

先完成[01环境安装](01-环境安装与运行.md)。本教程中的Git命令在**课程根目录的空闲终端窗口B**输入，不在Notebook代码单元、GitHub搜索框或运行Jupyter的窗口A输入。每条命令单独回车，成功后才执行下一条。

## 1. 先分清保存、提交、上传、合并

| 操作 | 改变哪里 | 是否已经进入课程main |
| --- | --- | --- |
| JupyterLab中Ctrl+S | 自己电脑的文件 | 否 |
| git add | 选择这次要交的文件 | 否 |
| git commit | 在本机保存一个有编号的版本 | 否 |
| git push | 把版本传到GitHub上的分支 | 否 |
| 创建Pull request（PR） | 请助教审阅并合并这组修改 | 否，仍待处理 |
| PR显示Merged | 修改已合并到目标分支 | 是，目标为课程main时 |

“分支”可以理解为本次任务的一条修改路线。每台电脑仍使用同一个课程文件夹，Git根据当前分支显示对应文件；切换前必须保存、关闭相关Notebook标签，防止浏览器把旧内容再次写回来。

## 2. 第一次配置：先确认自己把文件上传到哪里

在课程根目录输入：

```bash
git remote -v
```

`origin`是上传地址的简称。按下表选一条路线，**不要两条都做**。

| 情况 | 选择 |
| --- | --- |
| 已接受课程仓库的协作者邀请，origin是课程仓库 | 路线一，继续第3节 |
| 没有课程仓库写权限，希望从个人副本提交 | 路线二，先完成下方Fork设置 |

公开仓库允许查看和下载，不代表任何人能直接上传。账号密码只用于网页登录，不要在公开报告中填写。

### 路线二：没有写权限，先设置个人Fork

1. 登录GitHub，打开[课程仓库](https://github.com/prince19992516/-2026)，点击右上角 **Fork**，Owner选择自己，点击 **Create fork**。已经有自己的Fork就直接打开，不重复创建。
2. 在自己的副本中点绿色 **Code → HTTPS**，复制地址。地址的所有者应是自己，不是课程仓库所有者。
3. 已按01下载课程的同学继续用现有课程文件夹，不需要重新安装环境。下行中“你的GitHub用户名”必须换成自己的用户名；如果Fork改过仓库名，以刚复制的完整地址为准：

```bash
git remote set-url origin https://github.com/你的GitHub用户名/-2026.git
```

4. 再运行`git remote -v`，确认origin指向自己的Fork。将课程仓库添加为`upstream`，这个名字专门用于获取课程更新：

```bash
git remote add upstream https://github.com/prince19992516/-2026.git
```

5. 再运行`git remote -v`，应同时看到origin（自己的副本）和upstream（课程仓库）。提示`upstream already exists`时先检查已有地址；正确就继续，不重复添加。

以后**从upstream取得课程更新，向origin上传作业**。这两者不同；不要照搬有写权限同学的更新命令。

## 3. 设置本机提交身份，只需在这个副本设置一次

提交身份用于Git历史，和网页登录是两回事。下面引号中的内容必须换成自己的昵称和提交邮箱。可在GitHub个人 **Settings → Emails** 找到隐私用的noreply邮箱，完整复制，不要自己拼地址。

```bash
git config user.name "你的昵称"
```

```bash
git config user.email "你的GitHub提交邮箱"
```

公开分工表、报告和AI对话只填G编号，不填姓名、GitHub账号和私人联系方式；原始分组Excel不上传。Git的版本历史另外保存提交身份，所以这里可以用昵称与隐私邮箱。

## 4. 每次新任务：先更新main，再建自己的分支

在浏览器保存并关闭课程Notebook和文字编辑标签，回窗口B输入：

```bash
git status
```

看到`working tree clean`才继续。如果列出了modified、Untracked files或Changes to be committed，说明还有未保存成版本的改动：先在**当前任务分支**按第6节提交。安装练习造成的改动也不要不看内容就删除；不确定时保留并请助教协助。

切回main：

```bash
git switch main
```

**路线一（课程仓库协作者）**运行：

```bash
git pull --ff-only origin main
```

**路线二（Fork）**运行下面两条，不执行上面那条代替它：

```bash
git fetch upstream
```

```bash
git merge --ff-only upstream/main
```

成功后才新建任务分支。下面是**G22担任第01章A角色的真实示例**，其他组先改编号：

```bash
git switch -c chapter-01-a-g22
```

```bash
git branch --show-current
```

第二条应输出刚建的分支名，不再是main。各角色的实际示例见[08操作指南](08-各组具体操作指南.md)。提示分支已存在时，本次只是继续原任务就用`git switch 分支名`；新一轮任务则取新名字，如末尾加`-r2`，不要删除已有分支硬凑。

如果课程更新失败，不继续建分支。`--ff-only`失败说明本地与远程历史分叉；保留当前工作并请助教协助，不使用强推或reset清空历史。

## 5. 编辑、运行、保存：先按角色完成任务

回JupyterLab重新打开自己角色的文件，按[08操作指南](08-各组具体操作指南.md)填写。`.md`文件的编辑、Notebook运行与图片操作见[02写作教程](02-Notebook教材写作.md)。

同一章同一角色有两个小组：先约定小节/文件范围，各用自己的分支。报告按G编号分别记录，实验Notebook按小节约定交接；不要同时改同一段再互相覆盖。具体做法在08第一部分。

改了实验或验证代码时，重启内核、运行全部、核对实际结果，最后Ctrl+S。B/C遇到报错可以提交真实失败报告，不必把错误删除成“全部通过”。只修改排版的D/E也不需要伪称运行过所有实验。

## 6. 在本机保存一个版本

先运行`git status`，确认当前分支和本次修改的文件。以下仍以G22修改第一章的实验与编写报告为例，**只添加自己实际修改的文件**：

```bash
git add "教材/第01章-误差的代价/A组-实验.ipynb" "教材/第01章-误差的代价/A组-编写报告.md"
```

正文、习题、图片或AI记录也改了，就按相同写法分别`git add "相对路径"`。不要把字面上的“相对路径”当作文件名。相对路径从课程根目录开始；JupyterLab可右键文件选择Copy Path后核对。不要直接`git add .`把无关文件一起提交。

检查所选文件：

```bash
git diff --cached --stat
```

输出应只有这次准备交的文件。文本内容可用下面命令查看：

```bash
git diff --cached
```

显示较长、底部出现冒号或`(END)`时，按`q`退出查看，不是在文件里输入q。Notebook差异可能是JSON，回JupyterLab查看实际单元。选错文件时用`git restore --staged "实际文件路径"`取消暂存，文件内容仍保留；修改完文件后需重新git add。

确认后保存版本：

```bash
git commit -m "第01章 G22 A角色：补充误差实验与编写报告"
```

成功会显示版本编号与文件摘要。`nothing to commit`表示没有暂存的新内容，先核对是否Ctrl+S、是否git add，以及是否位于正确副本。`Author identity unknown`时回第3节设置身份，再执行commit。

## 7. 上传分支，并在网页创建PR

第一次上传当前分支：

```bash
git push -u origin HEAD
```

这里HEAD代表当前分支。执行前可用`git branch --show-current`确认没有留在main。以后同一分支补交修改，先add、commit，再`git push`即可。

若弹出登录窗口，使用有权访问目标origin的账号完成登录。出现403或`Permission denied`，先检查邀请是否接受、登录账号与origin地址；没有权限就按第2节Fork路线处理。不要反复输账号密码或把访问令牌写进文件。[GitHub上传说明](https://docs.github.com/en/get-started/using-git/pushing-commits-to-a-remote-repository)

上传成功后在浏览器操作：

1. 打开[课程仓库](https://github.com/prince19992516/-2026)，点击 **Pull requests → New pull request**。
2. 路线一：base选择`main`，compare选择刚上传的任务分支。
3. 路线二：点击 **compare across forks**，base repository选课程仓库、base选main；head repository选自己的Fork、compare选自己的任务分支。
4. 先查看 **Files changed** 或页面下方差异，确认没有别组被删除的内容、私人信息和环境文件。点击 **Create pull request**。
5. 标题写“第01章 G22 A角色：初稿/第1次修订”等。正文填写出现的PR模板：改了什么、报告在哪、运行了什么、还有什么没完成。不适用项直接写“不适用：原因”，不要为了全勾选而造假。
6. 点击最终的 **Create pull request**。若初稿未齐，可在按钮下拉选择 **Create draft pull request**（草稿PR），并写清尚未完成；准备好后再改为Ready for review。
7. 成功会进入一张带编号的PR页面，如`#123`。复制浏览器地址给需要复核的B/C和助教；不要把127.0.0.1的本机地址当提交链接。

PR里建议这样写，按实际情况替换，不直接交占位词：

```markdown
章节/组别/角色/轮次：第01章 / G22 / A / 初稿
本次范围：1.1节正文、对应实验和习题
报告位置：教材/第01章-误差的代价/A组-编写报告.md 中G22记录
实际运行：说明系统、内核、运行的Notebook与输出核对结果
尚未完成：列出未完成小节或问题；没有则说明已核对的范围
需要谁处理：对应B/C复核，或D/E统一格式
```

## 8. 给B/C一个确切版本，而不是“最新版”

在A的任务分支已经commit且push成功后执行：

```bash
git rev-parse HEAD
```

复制完整输出（本仓库是40位十六进制编号），连同PR链接、章节范围、额外依赖和待验证项给B/C。B报告完成后也这样给C提供自己的版本。新的commit会产生新编号；旧报告不能只把编号换成新的就算复测过。

B/C在自己的报告里写**被审内容版本**，不要求把报告自身尚未产生的编号写进自己。取得未合并PR、固定版本并运行的详细命令在[06复现教程](06-B组如何在干净环境复现.md)。

## 9. 收到修改意见后怎么继续

PR仍未合并时，在同一任务分支改文件、运行相关实验、保存、add、commit、push。原PR会自动出现新提交，通常不再新建一张。回复具体问题时写“修改位置、修复版本、实际复测结果”，不能只写“已改”。

PR合并后再收到新任务或修订要求：按第4节从更新后的main建新分支，如`chapter-01-a-g22-r2`。原PR已Merged时继续往旧分支push不会自动把新改动合入main。

自己的任务分支需要取得已合并的同角色另一组修改时：先保存并提交当前工作，关闭相关编辑标签，保持在**自己的任务分支**。路线一执行：

```bash
git fetch origin
```

```bash
git merge --no-edit origin/main
```

路线二（Fork）改为执行：

```bash
git fetch upstream
```

```bash
git merge --no-edit upstream/main
```

只选自己的路线。`--no-edit`使用默认合并说明，避免弹出额外文字编辑器；不会自动解决冲突。这是在任务分支合入最新课程内容，和第4节在main上更新不同。成功后重新打开文件、核对自己的内容与另一组内容均保留，受影响的Notebook重新运行保存，再提交和push。

若出现CONFLICT或unmerged，按下一节处理；冲突未解决前不继续提交新的实验结果。

## 10. 常见卡点

| 看见什么 | 先做什么 |
| --- | --- |
| 终端一直显示Jupyter日志，输入git没反应 | 打开空闲窗口B，在课程根目录输入命令 |
| not a git repository | 当前目录不对，回能看到course.cmd的课程根目录；ZIP下载不含Git历史 |
| git status显示文件名是反斜线和数字 | 可运行`git -c core.quotepath=false status`查看中文路径 |
| push报non-fast-forward/rejected | 可能另一人修改了同一远程分支；停止强推，核对分支并请助教协助合并 |
| PR没有可比较的修改 | 确认已经commit和push、选对compare分支，且不是已经合并的旧任务 |
| GitHub上看不到刚改的单元 | 依次确认Ctrl+S、add、commit、push；再确认网页正在查看自己的分支 |
| Notebook提示磁盘文件已变化 | 先保留未保存内容，停止重复保存旧标签；确认Git更新后版本，再重新打开 |
| 出现CONFLICT、`<<<<<<<`等标记 | 是版本冲突，不是数学错误；保留双方内容，联系同组/助教共同处理 |

Notebook是JSON，不宜直接随便删冲突标记。先保留双方副本，再在Jupyter中逐单元合并需要的内容，运行、核对、保存；不要简单选择“全部采用我的”丢弃另一组证据。初学者遇到冲突应保留现场并求助，不照抄网上的强制覆盖命令。

提交完成的判断：GitHub上能打开自己的PR，文件与报告齐全，状态清楚；合并完成的判断：页面显示Merged。两者不要混为一谈。
