import time
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Any, Union
import aiosqlite
import logfire
import win32com.client
from typing_extensions import TypeAlias
from pydantic_ai import Agent, ModelRetry, RunContext
from models import Success, InvalidRequest
from llms import model

logfire.configure(token="your logfire token")

DB_SCHEMA = """
CREATE TABLE test_requirements (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    requirements TEXT NOT NULL,
    tag INTEGER DEFAULT 0,
    date TEXT NOT NULL,
    submitter TEXT NOT NULL,
    importance TEXT NOT NULL,
    moduleName TEXT NOT NULL
);
"""


def extract_text_from_doc(file_path):
    try:
        word = win32com.client.Dispatch("Wps.Application")
    except:
        word = win32com.client.Dispatch("KWPS.Application")
    doc = word.Documents.Open(file_path)
    text = doc.Content.Text
    doc.Close()
    word.Quit()
    return text


@dataclass
class DBConnection:
    conn: aiosqlite.Connection


Response: TypeAlias = Union[Success, InvalidRequest]
agent: Agent = Agent(model=model, result_type=Response, deps_type=DBConnection)


@agent.system_prompt
async def system_prompt(ctx: RunContext[DBConnection]) -> str:
    doc_path = r'C:\develop\developfile\PythonProjects\Agent_testcase\doc\ERP（资源协同）管理平台需求说明书（商品管理部分）.doc'
    text = extract_text_from_doc(doc_path)
    # 从 ctx.deps 获取 ID 起始值
    start_id = getattr(ctx.deps, 'start_id', 1)
    return f"""
你是一名高级软件测试工程师，请根据如下的软件测试需求说明书，生成专业的、高覆盖的测试用例需求列表。
确保测试需求覆盖所有功能点，逻辑清晰，易于执行，且符合软件测试最佳实践。
最终编写出符合用户请求的sql语句，将需求写入数据库。
当前的时间为：{time.strftime('%Y-%m-%d')}

重要：ID 生成规则
- ID 必须从 {start_id} 开始，连续递增
- 每条 INSERT 语句的 ID 字段必须严格按照此规则递增：{start_id}, {start_id+1}, {start_id+2}, ...
- 请根据需求说明书的内容，生成合适数量的测试需求

数据库模式如下：
{DB_SCHEMA}

需求说明书如下：
{text}

请生成标准的 INSERT 语句，确保 ID 字段严格按照指定规则递增。
"""


@agent.result_validator
async def validate_result(ctx: RunContext[DBConnection], result: Response):
    if isinstance(result, InvalidRequest):
        return

    if not result.sql_query.upper().startswith('INSERT'):
        raise ModelRetry('请创建一个 INSERT 插入')

    try:
        await ctx.deps.conn.executescript(result.sql_query)
    except aiosqlite.Error as e:
        raise ModelRetry(f'无效的插入: {e}') from e
    else:
        return


@asynccontextmanager
async def connect_database(database: str) -> AsyncGenerator[Any, None]:
    # 完全移除span的使用
    conn = await aiosqlite.connect(database)
    try:
        yield conn
    finally:
        await conn.close()


def is_output_truncated(sql_query: str, expected_min_count: int = 5) -> bool:
    """
    检测输出是否被截断
    Args:
        sql_query: SQL查询字符串
        expected_min_count: 预期最少条数
    Returns:
        是否被截断
    """
    if not sql_query:
        return True
    
    # 检查是否以完整的分号结尾
    if not sql_query.strip().endswith(';') and not sql_query.strip().endswith(')'):
        return True
    
    # 检查INSERT语句数量是否过少
    insert_count = sql_query.count('INSERT INTO')
    if insert_count < expected_min_count:
        return False  # 数量少但可能是正常的
    
    # 检查最后一条INSERT是否完整
    last_insert_pos = sql_query.rfind('INSERT INTO')
    if last_insert_pos != -1:
        remaining = sql_query[last_insert_pos:]
        if not (remaining.count('(') == remaining.count(')') and remaining.endswith(';')):
            return True
    
    return False


async def run_agent(prompt: str, start_id: int = 1, max_batch_size: int = 20):
    """
    运行文档需求分析智能体，支持智能分批
    Args:
        prompt: 用户提示
        start_id: ID 起始值
        max_batch_size: 单批最大条数（用于分批时）
    Returns:
        生成的 SQL 语句列表
    """
    start_time = time.time()
    
    async with connect_database('.chat_app_db.sqlite') as conn:
        # 第一次尝试：一次性生成全部
        deps = DBConnection(conn)
        deps.start_id = start_id
        
        result = await agent.run(prompt, deps=deps)
        print("agent.run result:", result)
        print("agent.run data:", result.data)
        
        # 提取 SQL 查询
        sql_query = await extract_sql_from_result(result)
        
        if not sql_query:
            print("未获取到 sql_query 字段")
            return []
        
        # 检查是否被截断
        if not is_output_truncated(sql_query):
            # 输出完整，直接返回
            sqls = [s.strip() for s in sql_query.split(';') if s.strip()]
            elapsed = time.time() - start_time
            print(f"一次性生成完成，共 {len(sqls)} 条，耗时 {elapsed:.2f} 秒")
            return sqls
        
        print("检测到输出可能被截断，启动分批模式...")
        
        # 分批处理模式
        all_sqls = []
        current_id = start_id
        batch_num = 1
        
        while True:
            batch_start_time = time.time()
            # 简化批次提示词，避免复杂的上下文
            batch_prompt = f"{prompt}，请生成从ID {current_id} 开始的 {max_batch_size} 条记录。"
            
            deps = DBConnection(conn)  # 复用同一个连接
            deps.start_id = current_id
            deps.batch_size = max_batch_size
            
            result = await agent.run(batch_prompt, deps=deps)
            sql_query = await extract_sql_from_result(result)
            
            batch_elapsed = time.time() - batch_start_time
            
            if not sql_query:
                print(f"第 {batch_num} 批次未获取到数据，结束分批")
                break
            
            batch_sqls = [s.strip() for s in sql_query.split(';') if s.strip()]
            if not batch_sqls:
                print(f"第 {batch_num} 批次无有效SQL，结束分批")
                break
            
            all_sqls.extend(batch_sqls)
            current_id += len(batch_sqls)
            
            print(f"第 {batch_num} 批次完成，生成 {len(batch_sqls)} 条，累计 {len(all_sqls)} 条，耗时 {batch_elapsed:.2f} 秒")
            
            # 如果本批次生成数量少于预期，说明已经生成完毕
            if len(batch_sqls) < max_batch_size:
                print("本批次数量少于预期，推测已生成完毕")
                break
            
            batch_num += 1
            
            # 防止无限循环，减少最大批次限制
            if batch_num > 6:
                print("达到最大批次限制，结束分批")
                break
        
        total_elapsed = time.time() - start_time
        print(f"分批模式完成，总共生成 {len(all_sqls)} 条，总耗时 {total_elapsed:.2f} 秒")
        return all_sqls


async def extract_sql_from_result(result) -> str:
    """
    从 PydanticAI 结果中提取 SQL 查询
    """
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
    
    return sql_query