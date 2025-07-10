from typing import List, Annotated
from annotated_types import MinLen
from pydantic import BaseModel, Field
from dataclasses import dataclass


class TestCaseModel(BaseModel):
    id: str = Field(..., description="测试用例ID")
    title: str = Field(..., description="测试用例标题")
    description: str = Field(..., description="测试用例描述")
    precondition: str = Field(..., description="测试用例前置条件")
    priority: str = Field(..., description="测试用例优先级")
    steps: str = Field(..., description="测试用例步骤")
    actual_result: str = Field(..., description="测试用例实际结果")
    expected_result: str = Field(..., description="测试用例预期结果")
    test_type: str = Field(default="功能测试", description="测试类型：功能测试，性能测试，安全测试")


class TestCaseList(BaseModel):
    id: str = Field(..., description="需求ID")
    requirements_name: str = Field(..., description="需求名称")
    testcases: List[TestCaseModel] = Field(..., description="测试用例列表")


class Success(BaseModel):
    """成功生成 SQL 时的响应"""

    sql_query: Annotated[str, MinLen(1)]  # 生成的 SQL 查询
    explanation: str = Field(
        '', description='SQL 查询的解释，以 Markdown 格式'
    )
    requirements_list: List = Field(
        default_factory=lambda: list,
        description='查询结果，以列表形式返回，列表中的每个元素是一个元组'
    )

class InvalidRequest(BaseModel):
    """用户输入的信息不足以生成 SQL 时的响应"""

    error_message: str  # 错误消息

@dataclass
class DocAgentDeps:
    doc_path: str
    db_path: str

@dataclass
class SqlAgentDeps:
    db_path: str
    filter: str

@dataclass
class TestcaseAgentDeps:
    db_path: str
    excel_path: str
    filter: str
    prompt: str
    total: int = 30
    batch_size: int = 10
    requirements_list: list = None
