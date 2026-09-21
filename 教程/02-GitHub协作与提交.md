# 02 GitHub协作与提交

## 第一次准备
注册GitHub账号，安装Git，在仓库根目录配置自己的提交身份：

```bash
git config user.name "你的姓名或昵称"
git config user.email "你的GitHub提交邮箱"
git switch main
git pull --ff-only origin main
git switch -c chapter-01-a-yourname
```

分支名示例中01是章节，a是组别。B/C分别用b/c；每次新任务从更新后的main建立新分支。

## 修改、检查、提交

关闭其他人同时编辑的Notebook，只修改本组负责的文件。下面以A组第一章为例：

```bash
python 脚本/检查笔记本.py 教材/第01章-误差
python 脚本/检查结构.py
git status
git add 教材/第01章-误差/实验.ipynb 教材/第01章-误差/编写报告.md
git diff --cached --stat
git commit -m "第01章 A组：补充误差实验与编写报告"
git push -u origin chapter-01-a-yourname
```

上面只暂存两个示范文件；本次修改了正文、习题等文件时逐个加入。不要把 `.venv`、密钥、运行缓存和无关资料一并上传。

在GitHub仓库打开 **Pull requests → New pull request**，base选main，compare选自己的分支。填写PR模板和报告链接，查看Actions结果，按审阅意见继续在同一分支提交即可。合并通常由助教负责。

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
