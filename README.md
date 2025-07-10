# 软件测试工程师智能体系统

一个专业的软件测试工程师AI助手，专门用于软件测试相关知识交流和测试用例生成系统管理。

## 🎯 系统功能

- **智能对话**: 与测试专家进行专业咨询
- **测试用例评审**: 自动评审测试用例质量
- **测试策略设计**: 智能生成测试策略和方案
- **系统管理**: 管理测试用例生成流程

## 💼 核心组件

- **test_engineer_agent.py**: 测试工程师智能体核心实现
- **test_engineer_gui.py**: 图形用户界面
- **gui_main.py**: 主界面实现
- **Sql_agent.py**: SQL交互组件
- **Testcase_agent.py**: 测试用例生成组件
- **DocAGTest.py**: 文档分析组件
- **models.py**: 数据模型定义
- **llms.py**: 大语言模型集成

## 🚀 安装与使用

### 环境要求

- Python 3.10+
- 依赖库: PyQt5, pydantic-ai, pandas, openpyxl, logfire, httpx

### 安装步骤

1. 克隆代码库
```bash
git clone https://github.com/yourusername/software-test-engineer-agent.git
cd software-test-engineer-agent
```

2. 安装依赖
```bash
pip install -r requirements.txt
```
3.设置密钥和日志令牌
在llms中设置你的大模型API密钥和sdk定位符：
```
model = OpenAIModel(
    model_name="qwen-max",
    api_key="your API key",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    http_client=http_client
)
```
在每个智能体模块中设置logfire日志令牌：
```
logfire.configure(token="your logfire token")
```

4. 启动系统
```bash
python start_system.py
```

### 主要功能模块

1. **测试咨询模块**
   - 专业测试方法和技术指导
   - 测试流程优化建议
   - 工具选型和使用建议

2. **用例评审模块**
   - 测试用例质量评估
   - 自动化评审与建议
   - 多维度质量分析

3. **测试策略模块**
   - 需求分析与风险评估
   - 测试方法选择指导
   - 资源规划与进度安排

## 📁 文件结构

```
├── test_engineer_agent.py    # 核心智能体实现
├── test_engineer_gui.py      # 智能体GUI界面
├── gui_main.py               # 主GUI界面
├── start_system.py           # 系统启动脚本
├── models.py                 # 数据模型定义
├── llms.py                   # LLM模型集成
├── Sql_agent.py              # SQL查询智能体
├── Testcase_agent.py         # 测试用例生成智能体
├── DocAGTest.py              # 文档分析智能体
├── sql/                      # SQL相关文件
│   └── requirements.sql      # 需求数据库结构
├── Exel/                     # Excel数据文件
│   └── *.xlsx                # 测试数据文件
└── doc/                      # 文档资源
    └── *.doc                 # 需求文档
```

## 📊 功能特色

- **专业性**: 集成专业测试工程师知识体系，提供高质量建议
- **智能化**: 利用大语言模型提供上下文感知的专业回答
- **可视化**: 直观的GUI界面，便于操作和使用
- **自动化**: 测试用例自动生成和评审

## 🤝 贡献指南

欢迎贡献代码、报告问题或提出改进建议！请遵循以下步骤：

1. Fork 项目仓库
2. 创建您的特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交您的更改 (`git commit -m 'Add some AmazingFeature'`)
4. 将更改推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建Pull Request

## 📄 许可证

项目采用 MIT 许可证 - 查看 LICENSE 文件了解更多细节 