@echo off
REM 软件测试工程师智能体系统GitHub推送脚本

echo ===== 软件测试工程师智能体系统 GitHub推送脚本 =====
echo 此脚本将帮助您将项目推送到GitHub

REM 检查是否安装git
where git >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo 错误: 未安装Git，请先安装Git: https://git-scm.com/downloads
    pause
    exit /b
)

REM 检查是否已初始化git仓库
if not exist ".git" (
    echo 正在初始化Git仓库...
    git init
)

REM 询问GitHub仓库信息
set /p github_username=请输入您的GitHub用户名: 
set /p repo_name=请输入您要创建的仓库名称(建议: software-test-engineer-agent): 

REM 添加所有文件到git
echo 正在添加文件到Git...
git add .

REM 提交更改
echo 正在提交更改...
git commit -m "初始化软件测试工程师智能体系统"

REM 添加GitHub远程仓库
echo 正在添加GitHub远程仓库...
git remote add origin "https://github.com/%github_username%/%repo_name%.git"

REM 推送到GitHub
echo 正在推送到GitHub...
echo 注意: 您可能需要输入GitHub凭据
git push -u origin master

echo.
echo ===== 操作完成 =====
echo 请检查您的GitHub仓库: https://github.com/%github_username%/%repo_name%
echo.
echo 如果推送失败，可以手动执行以下命令：
echo git push -u origin master
echo.
echo 如果您在GitHub上创建了仓库时添加了README.md，可能需要先合并：
echo git pull origin master --allow-unrelated-histories
echo.
echo 祝您使用愉快！

pause 