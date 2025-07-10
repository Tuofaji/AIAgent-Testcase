"""
软件测试工程师智能体

专业身份定位：
- 高级软件测试工程师 / 测试架构师
- 测试用例生成系统管理专家
- 测试流程优化顾问
- 质量保证专家

核心职责：
1. 管理和优化测试用例生成系统
2. 提供专业的软件测试咨询和指导
3. 设计测试策略和测试方案
4. 监控和改进测试流程
5. 培训和指导测试团队

技术专长：
- 测试理论与方法论
- 自动化测试设计
- 测试用例设计技术
- 缺陷管理和分析
- 测试工具使用和优化
"""

import json
import asyncio
from typing import List, Dict, Optional
from datetime import datetime
import pandas as pd
from pydantic_ai import Agent, RunContext
from pydantic import BaseModel, Field
from dataclasses import dataclass
from llms import model
import logfire

logfire.configure(token="your logfire token")

# 专业领域知识库
TEST_KNOWLEDGE_BASE = {
    "测试设计技术": {
        "黑盒测试": ["等价类划分", "边界值分析", "判定表", "状态转换", "因果图"],
        "白盒测试": ["语句覆盖", "分支覆盖", "条件覆盖", "路径覆盖", "修改条件决策覆盖"],
        "经验测试": ["探索性测试", "错误推测法", "场景测试", "用户体验测试"]
    },
    "测试类型": {
        "功能测试": ["单元测试", "集成测试", "系统测试", "验收测试"],
        "非功能测试": ["性能测试", "安全测试", "兼容性测试", "可用性测试", "可靠性测试"],
        "变更测试": ["冒烟测试", "回归测试", "确认测试"]
    },
    "测试流程": {
        "测试计划": ["需求分析", "测试策略", "资源规划", "风险评估"],
        "测试设计": ["用例设计", "数据准备", "环境搭建", "工具选型"],
        "测试执行": ["用例执行", "缺陷跟踪", "结果记录", "进度监控"],
        "测试总结": ["结果分析", "质量评估", "改进建议", "经验总结"]
    },
    "质量模型": {
        "ISO25010": ["功能性", "性能效率", "兼容性", "可用性", "可靠性", "安全性", "维护性", "可移植性"],
        "测试金字塔": ["单元测试（底层）", "集成测试（中层）", "UI测试（顶层）"]
    }
}

# 测试用例质量评估标准
TESTCASE_QUALITY_CRITERIA = {
    "完整性": ["前置条件清晰", "步骤详细", "预期结果明确", "数据准备充分"],
    "准确性": ["逻辑正确", "场景真实", "结果可验证", "数据有效"],
    "覆盖性": ["需求覆盖", "功能覆盖", "场景覆盖", "边界覆盖"],
    "可执行性": ["步骤可操作", "环境可搭建", "数据可获取", "结果可观察"],
    "可维护性": ["描述清晰", "结构合理", "依赖明确", "更新方便"]
}

@dataclass
class TestEngineerDeps:
    """测试工程师智能体依赖"""
    query_type: str = "consultation"  # consultation, testcase_review, strategy_design
    context: str = ""
    test_data: Optional[Dict] = None
    requirements: Optional[List] = None

class TestStrategy(BaseModel):
    """测试策略模型"""
    test_objectives: List[str] = Field(..., description="测试目标")
    test_scope: str = Field(..., description="测试范围")
    test_approach: List[str] = Field(..., description="测试方法")
    risk_assessment: List[str] = Field(..., description="风险评估")
    resource_planning: Dict[str, str] = Field(..., description="资源规划")
    timeline: str = Field(..., description="时间计划")

class TestCaseReview(BaseModel):
    """测试用例评审结果"""
    overall_score: int = Field(..., description="总体评分(1-10)")
    strengths: List[str] = Field(..., description="优点")
    weaknesses: List[str] = Field(..., description="不足")
    improvements: List[str] = Field(..., description="改进建议")
    quality_assessment: Dict[str, int] = Field(..., description="质量评估各维度得分")

class TestConsultation(BaseModel):
    """测试咨询回复"""
    professional_advice: str = Field(..., description="专业建议")
    best_practices: List[str] = Field(..., description="最佳实践")
    recommended_tools: List[str] = Field(..., description="推荐工具")
    learning_resources: List[str] = Field(..., description="学习资源")

# 初始化软件测试工程师智能体
test_engineer_agent = Agent(
    model=model,
    deps_type=TestEngineerDeps,
    result_type=str  # 根据不同查询类型返回不同结果
)

@test_engineer_agent.system_prompt
async def test_engineer_system_prompt(ctx: RunContext[TestEngineerDeps]) -> str:
    base_prompt = f"""
你是一名资深的软件测试工程师和测试架构师，拥有15年以上的软件测试经验。

🎯 **专业身份**：
- 高级软件测试工程师 / 测试架构师
- 测试用例生成系统管理专家  
- 测试流程优化顾问
- 质量保证专家

💼 **核心职责**：
1. 管理和优化测试用例生成系统
2. 提供专业的软件测试咨询和指导
3. 设计测试策略和测试方案
4. 监控和改进测试流程
5. 培训和指导测试团队

🏆 **技术专长**：
- 精通各种测试设计技术（黑盒、白盒、灰盒测试）
- 熟练掌握自动化测试框架和工具
- 具备丰富的测试用例设计和优化经验
- 擅长测试流程改进和质量管理
- 具备敏捷测试和DevOps测试实践经验

📚 **知识体系**：
{json.dumps(TEST_KNOWLEDGE_BASE, ensure_ascii=False, indent=2)}

🔍 **质量评估标准**：
{json.dumps(TESTCASE_QUALITY_CRITERIA, ensure_ascii=False, indent=2)}

当前查询类型：{ctx.deps.query_type}
"""
    
    if ctx.deps.query_type == "consultation":
        return base_prompt + """
        
🗣️ **咨询模式**：
作为测试咨询专家，我将为您提供：
- 专业的测试方法和技术指导
- 测试流程优化建议
- 工具选型和使用建议
- 测试团队建设指导
- 质量管理最佳实践

请详细描述您的问题，我会基于专业经验为您提供针对性的解决方案。
"""
    
    elif ctx.deps.query_type == "testcase_review":
        return base_prompt + """
        
📋 **测试用例评审模式**：
作为测试用例质量专家，我将从以下维度评审测试用例：

1. **完整性评估**：检查前置条件、执行步骤、预期结果是否完整
2. **准确性评估**：验证测试逻辑是否正确、场景是否真实
3. **覆盖性评估**：分析需求覆盖度、功能覆盖度、场景覆盖度
4. **可执行性评估**：确认步骤是否可操作、环境是否可搭建
5. **可维护性评估**：检查描述清晰度、结构合理性

请提供需要评审的测试用例，我会给出详细的评估报告和改进建议。
"""
    
    elif ctx.deps.query_type == "strategy_design":
        return base_prompt + """
        
🎯 **测试策略设计模式**：
作为测试架构师，我将帮您设计全面的测试策略：

1. **需求分析**：深入理解业务需求和质量目标
2. **风险评估**：识别项目风险和质量风险点
3. **测试方法选择**：选择合适的测试设计技术和测试类型
4. **资源规划**：人员配置、工具选型、环境规划
5. **进度安排**：制定合理的测试时间计划
6. **质量标准**：定义明确的质量评估标准

请提供项目背景信息，我会为您设计专业的测试策略。
"""
    
    else:
        return base_prompt + """
        
💬 **智能对话模式**：
我是您的专业测试顾问，可以为您提供：
- 测试技术咨询
- 用例设计指导  
- 流程优化建议
- 工具推荐
- 质量管理指导

有什么测试相关的问题，请随时向我咨询！
"""

class SoftwareTestEngineerAgent:
    """软件测试工程师智能体管理类"""
    
    def __init__(self):
        self.agent = test_engineer_agent
        self.session_history = []
        self.current_project = None
        
    async def consultation(self, question: str, context: str = "") -> TestConsultation:
        """测试咨询服务"""
        deps = TestEngineerDeps(
            query_type="consultation",
            context=context
        )
        
        prompt = f"""
作为资深测试工程师，请回答以下测试相关问题：

问题：{question}
上下文：{context if context else '无特殊上下文'}

请提供专业的建议，包括：
1. 针对性的专业建议
2. 相关的最佳实践
3. 推荐的工具或方法
4. 学习资源或参考资料

请以JSON格式返回，包含以下字段：
{{
    "professional_advice": "详细的专业建议",
    "best_practices": ["最佳实践1", "最佳实践2", ...],
    "recommended_tools": ["工具1", "工具2", ...],
    "learning_resources": ["资源1", "资源2", ...]
}}
"""
        
        result = await self.agent.run(prompt, deps=deps)
        return self._parse_consultation_result(result.data)
    
    async def review_testcases(self, test_cases: List[Dict]) -> TestCaseReview:
        """测试用例评审服务"""
        deps = TestEngineerDeps(
            query_type="testcase_review",
            test_data={"test_cases": test_cases}
        )
        
        prompt = f"""
请作为测试专家评审以下测试用例：

测试用例数据：
{json.dumps(test_cases, ensure_ascii=False, indent=2)}

请从以下维度进行评审：
1. 完整性（前置条件、步骤、预期结果是否完整）
2. 准确性（逻辑是否正确、场景是否真实）
3. 覆盖性（需求覆盖、功能覆盖、场景覆盖）
4. 可执行性（步骤是否可操作）
5. 可维护性（描述是否清晰）

请提供详细的评审结果，包括：
1. 总体评分
2. 优点和不足
3. 改进建议
4. 每个维度的评分

你可以选择以下两种格式之一返回评审结果：

1. JSON格式（简洁）：
{{
    "overall_score": 评分(1-10),
    "strengths": ["优点1", "优点2", ...],
    "weaknesses": ["不足1", "不足2", ...],
    "improvements": ["改进建议1", "改进建议2", ...],
    "quality_assessment": {{
        "完整性": 评分(1-10),
        "准确性": 评分(1-10),
        "覆盖性": 评分(1-10),
        "可执行性": 评分(1-10),
        "可维护性": 评分(1-10)
    }}
}}

2. 详细评审格式（包含更多细节）：
首先提供JSON格式的摘要，然后提供每个维度的详细评审，包括优点、不足和具体的改进建议。
"""
        
        result = await self.agent.run(prompt, deps=deps)
        
        # 如果结果是字符串，可能是详细评审结果
        if isinstance(result.data, str):
            return result.data
            
        return self._parse_review_result(result.data)
    
    async def design_test_strategy(self, project_info: Dict) -> TestStrategy:
        """设计测试策略"""
        deps = TestEngineerDeps(
            query_type="strategy_design",
            context=json.dumps(project_info, ensure_ascii=False)
        )
        
        prompt = f"""
请为以下项目设计全面的测试策略：

项目信息：
{json.dumps(project_info, ensure_ascii=False, indent=2)}

请设计包含以下内容的测试策略：
1. 测试目标
2. 测试范围
3. 测试方法和技术
4. 风险评估
5. 资源规划
6. 时间计划

请以JSON格式返回：
{{
    "test_objectives": ["目标1", "目标2", ...],
    "test_scope": "测试范围描述",
    "test_approach": ["方法1", "方法2", ...],
    "risk_assessment": ["风险1", "风险2", ...],
    "resource_planning": {{
        "人员": "人员规划",
        "工具": "工具规划",
        "环境": "环境规划"
    }},
    "timeline": "时间计划描述"
}}
"""
        
        result = await self.agent.run(prompt, deps=deps)
        return self._parse_strategy_result(result.data)
    
    async def chat(self, message: str) -> str:
        """智能对话"""
        deps = TestEngineerDeps(
            query_type="chat",
            context=message
        )
        
        # 添加专业身份提醒
        prompt = f"""
用户消息：{message}

请以专业的软件测试工程师身份回复，确保：
1. 体现专业的测试知识和经验
2. 提供实用的建议和指导
3. 语言专业而友好
4. 必要时提供具体的操作建议或最佳实践

如果用户询问的是测试用例生成系统相关问题，请强调您作为测试用例生成系统管理专家的专业性。
"""
        
        result = await self.agent.run(prompt, deps=deps)
        return result.data
    
    def _parse_consultation_result(self, result_str: str) -> TestConsultation:
        """解析咨询结果"""
        try:
            data = json.loads(result_str)
            return TestConsultation(**data)
        except:
            # 如果解析失败，返回默认结构
            return TestConsultation(
                professional_advice=result_str,
                best_practices=[],
                recommended_tools=[],
                learning_resources=[]
            )
    
    def _parse_review_result(self, result_str: str) -> TestCaseReview:
        """解析评审结果"""
        try:
            # 如果结果是字符串，且包含详细评审结果，直接返回
            if isinstance(result_str, str) and ("详细评审结果" in result_str or "```json" in result_str):
                return result_str
                
            # 尝试解析JSON
            data = json.loads(result_str) if isinstance(result_str, str) else result_str
            return TestCaseReview(**data)
        except Exception as e:
            print(f"解析评审结果出错: {str(e)}")
            # 如果解析失败但结果是字符串，直接返回
            if isinstance(result_str, str):
                return result_str
                
            # 返回默认结构
            return TestCaseReview(
                overall_score=7,
                strengths=["结构清晰"],
                weaknesses=["需要更多细节"],
                improvements=["请提供更详细的测试步骤"],
                quality_assessment={"完整性": 7, "准确性": 7, "覆盖性": 7, "可执行性": 7, "可维护性": 7}
            )
    
    def _parse_strategy_result(self, result_str: str) -> TestStrategy:
        """解析策略结果"""
        try:
            data = json.loads(result_str)
            return TestStrategy(**data)
        except:
            return TestStrategy(
                test_objectives=["确保软件质量"],
                test_scope="全功能测试",
                test_approach=["功能测试", "性能测试"],
                risk_assessment=["进度风险", "质量风险"],
                resource_planning={"人员": "2-3名测试工程师", "工具": "自动化测试工具", "环境": "测试环境"},
                timeline="4周测试周期"
            )

# 创建全局实例
software_test_engineer = SoftwareTestEngineerAgent()

# 便捷函数
async def ask_test_expert(question: str, context: str = "") -> str:
    """向测试专家咨询"""
    result = await software_test_engineer.consultation(question, context)
    return f"""
🎯 专业建议：
{result.professional_advice}

💡 最佳实践：
{chr(10).join([f"• {practice}" for practice in result.best_practices])}

🛠️ 推荐工具：
{chr(10).join([f"• {tool}" for tool in result.recommended_tools])}

📚 学习资源：
{chr(10).join([f"• {resource}" for resource in result.learning_resources])}
"""

async def review_my_testcases(test_cases: List[Dict]) -> str:
    """评审测试用例"""
    result = await software_test_engineer.review_testcases(test_cases)
    
    # 检查结果是否为字符串，如果是，可能是详细评审结果
    if isinstance(result, str) and ("详细评审结果" in result or "```json" in result):
        return result
    
    # 返回原始JSON字符串
    import json
    return json.dumps({
        "overall_score": result.overall_score,
        "strengths": result.strengths,
        "weaknesses": result.weaknesses,
        "improvements": result.improvements,
        "quality_assessment": result.quality_assessment
    }, ensure_ascii=False)

async def chat_with_test_engineer(message: str) -> str:
    """与测试工程师对话"""
    return await software_test_engineer.chat(message)

if __name__ == "__main__":
    # 示例使用
    async def demo():
        print("🤖 软件测试工程师智能体启动")
        print("=" * 50)
        
        # 咨询示例
        print("\n1. 测试咨询示例：")
        advice = await ask_test_expert(
            "如何设计一个电商系统的测试方案？",
            "项目是一个中型电商平台，包含用户管理、商品管理、订单管理等模块"
        )
        print(advice)
        
        # 对话示例
        print("\n2. 智能对话示例：")
        response = await chat_with_test_engineer("你好，我是新入职的测试工程师，请介绍一下测试用例生成系统")
        print(response)
    
    # 运行示例
    asyncio.run(demo()) 