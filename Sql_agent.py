import asyncio
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Any, Union, List
import aiosqlite
import logfire
from typing_extensions import TypeAlias
from pydantic_ai import Agent, ModelRetry, RunContext
from models import Success, InvalidRequest
from llms import model

logfire.configure(token="your logfire token")

DB_SCHEMA = """
CREATE TABLE test_requirements (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    requirements TEXT NOT NULL, -- 软件测试需求内容
    tag INTEGER DEFAULT 0, -- 0: 未完成, 1: 已完成
    date TEXT NOT NULL,    -- 日期格式: YYYY-MM-DD
    submitter TEXT NOT NULL, -- 提交人: 田老师, 助教小姐姐, 但问智能
    importance TEXT NOT NULL,
    moduleName TEXT NOT NULL
);
"""


@dataclass
class DBConnection:
    conn: aiosqlite.Connection  # SQLite 数据库连接

Response: TypeAlias = Union[Success, InvalidRequest]  # 响应类型别名
agent: Agent = Agent(model=model, result_type=Response, deps_type=DBConnection,)


@agent.system_prompt
async def system_prompt(ctx: RunContext[DBConnection]) -> str:
    # 从 ctx.deps 获取 ID 相关参数
    start_id = getattr(ctx.deps, 'start_id', 1)
    filter_text = getattr(ctx.deps, 'filter', '')
    return f'''
你是SQL专家。请根据用户请求，生成只包含SELECT的SQL查询，并返回如下JSON格式：
{{
  "sql_query": "SELECT ...",
  "explanation": "本查询的解释",
  "requirements_list": []
}}

数据库模式：
CREATE TABLE test_requirements (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    requirements TEXT NOT NULL,
    tag INTEGER DEFAULT 0,
    date TEXT NOT NULL,
    submitter TEXT NOT NULL,
    importance TEXT NOT NULL,
    moduleName TEXT NOT NULL
);

重要规则：
1. 只允许SELECT，禁止分号、注释、union等危险语句
2. 表名是 test_requirements，不是 requirements
3. 如果查询涉及 ID 筛选，当前数据库中的 ID 从 {start_id} 开始
4. 请根据用户需求生成合适的查询条件

用户请求：{filter_text}
'''


@agent.result_validator
async def validate_result(ctx: RunContext[DBConnection], result: Response) -> Response:
    if isinstance(result, InvalidRequest):
        return result

    if not result.sql_query.upper().startswith('SELECT'):
        raise ModelRetry('请创建一个 SELECT 查询')

    try:
        await ctx.deps.conn.execute(f'EXPLAIN QUERY PLAN {result.sql_query}')
    except aiosqlite.Error as e:
        raise ModelRetry(f'无效的查询: {e}') from e
    else:
        return result

@agent.tool
async def execute_sql(ctx: RunContext[DBConnection], result: Response) -> List:
    """执行 SQL 查询并返回结果"""
    data = await ctx.deps.conn.execute_fetchall(result.sql_query)
    return data

@asynccontextmanager
async def connect_database(database: str) -> AsyncGenerator[Any, None]:
    with logfire.span('连接数据库'):
        conn = await aiosqlite.connect(database)
        try:
            yield conn
        finally:
            await conn.close()


async def run_agent(prompt: str, db_path: str = None, filter: str = None, start_id: int = 1):
    """
    运行 SQL 查询智能体
    Args:
        prompt: 用户提示
        db_path: 数据库路径
        filter: 查询过滤条件
        start_id: ID 起始值（用于提示模型当前数据范围）
    Returns:
        查询结果的需求列表
    """
    async with connect_database(db_path) as conn:
        # 创建带 ID 信息的依赖对象
        deps = DBConnection(conn)
        deps.filter = filter
        deps.start_id = start_id
        
        result = await agent.run(prompt, deps=deps)
        print("agent.run result:", result)
        print("agent.run data:", result.data)
        
        # 尝试多种方式获取 sql_query
        sql_query = None
        output = result.data
        
        if output and hasattr(output, 'sql_query'):
            sql_query = output.sql_query
        elif output and isinstance(output, dict) and 'sql_query' in output:
            sql_query = output['sql_query']
        else:
            # 如果 data 是 None，尝试从 tool call 中提取
            for message in result._all_messages:
                if hasattr(message, 'parts'):
                    for part in message.parts:
                        if hasattr(part, 'tool_name') and 'Success' in part.tool_name and hasattr(part, 'args'):
                            try:
                                import json
                                args_data = json.loads(part.args)
                                if 'sql_query' in args_data:
                                    sql_query = args_data['sql_query']
                                    break
                            except:
                                continue
                if sql_query:
                    break
        
        if not sql_query:
            print("未获取到 sql_query 字段，data:", output)
            return []
        
        print(f"生成的SQL查询: {sql_query}")
        
        # 执行 SQL 查询获取实际数据
        try:
            cursor = await conn.execute(sql_query)
            rows = await cursor.fetchall()
            await cursor.close()
            
            # 将查询结果转换为需求列表
            requirements_list = []
            for row in rows:
                # 假设表结构：ID, requirements, tag, date, submitter, importance, moduleName
                requirement_data = {
                    'ID': row[0],
                    'requirements': row[1],
                    'tag': row[2],
                    'date': row[3],
                    'submitter': row[4],
                    'importance': row[5],
                    'moduleName': row[6]
                }
                requirements_list.append(requirement_data)
            
            print(f"查询到 {len(requirements_list)} 条需求数据")
            
            # 为了向后兼容，返回需求文本列表
            requirement_texts = [req['requirements'] for req in requirements_list]
            return requirement_texts
            
        except Exception as e:
            print(f"执行SQL查询失败: {e}")
            return []