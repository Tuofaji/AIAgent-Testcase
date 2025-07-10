#!/bin/bash
# 软件测试工程师智能体系统GitHub推送脚本

echo "===== 软件测试工程师智能体系统 GitHub推送脚本 ====="
echo "此脚本将帮助您将项目推送到GitHub"

# 检查是否安装git
if ! command -v git &> /dev/null; then
    echo "错误: 未安装Git，请先安装Git: https://git-scm.com/downloads"
    exit 1
fi

# 检查是否已初始化git仓库
if [ ! -d ".git" ]; then
    echo "正在初始化Git仓库..."
    git init
fi

# 询问GitHub仓库信息
read -p "请输入您的GitHub用户名: " github_username
read -p "请输入您要创建的仓库名称(建议: software-test-engineer-agent): " repo_name

# 更新README.md中的仓库链接
sed -i "s|yourusername|$github_username|g" README.md
sed -i "s|yourusername|$github_username|g" CONTRIBUTING.md

# 添加所有文件到git
echo "正在添加文件到Git..."
git add .

# 提交更改
echo "正在提交更改..."
git commit -m "初始化软件测试工程师智能体系统"

# 添加GitHub远程仓库
echo "正在添加GitHub远程仓库..."
git remote add origin "https://github.com/$github_username/$repo_name.git"

# 推送到GitHub
echo "正在推送到GitHub..."
echo "注意: 您可能需要输入GitHub凭据"
git push -u origin master

echo ""
echo "===== 操作完成 ====="
echo "请检查您的GitHub仓库: https://github.com/$github_username/$repo_name"
echo ""
echo "如果推送失败，可以手动执行以下命令："
echo "git push -u origin master"
echo ""
echo "如果您在GitHub上创建了仓库时添加了README.md，可能需要先合并："
echo "git pull origin master --allow-unrelated-histories"
echo ""
echo "祝您使用愉快！" 