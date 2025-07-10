"""
测试用例生成智能体

调参说明：
- 如果发现批次处理仍然变慢，可以调整BATCH_CONFIG中的参数
- 监控性能总结输出，识别哪个批次处理时间异常
- 对于大量测试用例生成，建议适当增加max_batch_size减少批次数量
"""

import json
import os
import asyncio
from typing import List, Dict
import pandas as pd
import logfire
from openpyxl.reader.excel import load_workbook
from pydantic_ai import Agent, RunContext
from models import TestcaseAgentDeps
from llms import model
from openai import InternalServerError, APITimeoutError, RateLimitError

logfire.configure(token="your logfire token")

# 批次处理优化配置
BATCH_CONFIG = {
    "max_retries": 1,  # 减少重试次数，避免等待时间累积
    "base_delay": 1,   # 减少基础延迟时间
    "max_batch_limit": 6,  # 减少最大批次数量
    "performance_warning_threshold": 30,  # 批次时间警告阈值（秒）
    "target_completion_ratio": 0.8,  # 目标完成度（80%即认为完成）
}

class BatchPerformanceMonitor:
    """批次性能监控器"""
    def __init__(self):
        self.batch_times = []
        self.batch_sizes = []
        self.total_start_time = None
    
    def start_total_timing(self):
        """开始总计时"""
        import time
        self.total_start_time = time.time()
    
    def record_batch(self, batch_num: int, batch_size: int, elapsed_time: float):
        """记录批次性能"""
        self.batch_times.append(elapsed_time)
        self.batch_sizes.append(batch_size)
        
        # 计算平均时间和趋势
        if len(self.batch_times) > 1:
            avg_time = sum(self.batch_times) / len(self.batch_times)
            recent_avg = sum(self.batch_times[-3:]) / min(3, len(self.batch_times))
            
            if recent_avg > avg_time * 1.5:
                print(f"⚠️  警告：第 {batch_num} 批次处理时间 ({elapsed_time:.2f}s) 明显超出平均时间 ({avg_time:.2f}s)")
            elif elapsed_time > BATCH_CONFIG["performance_warning_threshold"]:
                print(f"⚠️  警告：第 {batch_num} 批次处理时间过长 ({elapsed_time:.2f}s)")
    
    def get_summary(self):
        """获取性能总结"""
        if not self.batch_times:
            return "无批次数据"
        
        import time
        total_time = time.time() - self.total_start_time if self.total_start_time else 0
        avg_batch_time = sum(self.batch_times) / len(self.batch_times)
        max_time = max(self.batch_times)
        min_time = min(self.batch_times)
        
        return f"""
📊 批次性能总结:
   - 总批次数: {len(self.batch_times)}
   - 总耗时: {total_time:.2f} 秒
   - 平均批次时间: {avg_batch_time:.2f} 秒
   - 最快批次: {min_time:.2f} 秒
   - 最慢批次: {max_time:.2f} 秒
   - 时间趋势: {'递增' if len(self.batch_times) > 2 and self.batch_times[-1] > self.batch_times[0] else '稳定'}
        """

# 全局性能监控器
performance_monitor = BatchPerformanceMonitor()

async def retry_with_backoff(func, max_retries=2, base_delay=1):
    """
    带有指数退避的重试机制
    Args:
        func: 要重试的异步函数
        max_retries: 最大重试次数（减少重试次数）
        base_delay: 基础延迟时间（秒）（减少基础延迟）
    Returns:
        函数执行结果
    """
    for attempt in range(max_retries + 1):
        try:
            return await func()
        except (InternalServerError, APITimeoutError, RateLimitError) as e:
            if attempt == max_retries:
                print(f"重试 {max_retries} 次后仍然失败: {e}")
                raise
            
            # 使用线性退避而不是指数退避，避免后续批次等待过久
            delay = base_delay * (attempt + 1)  # 线性退避：1, 2, 3...
            print(f"API调用失败 (尝试 {attempt + 1}/{max_retries + 1}): {e}")
            print(f"等待 {delay} 秒后重试...")
            await asyncio.sleep(delay)
        except Exception as e:
            # 非API相关错误，直接抛出
            print(f"非API错误，不重试: {e}")
            raise

def optimize_requirements_text(requirements_list, max_length=1000):
    """
    优化需求文本长度，避免提示词过长导致超时
    Args:
        requirements_list: 需求列表
        max_length: 最大字符长度
    Returns:
        优化后的需求文本
    """
    if not requirements_list:
        return "注意：未获取到具体需求列表，请基于商品管理模块的常见功能生成测试用例。"
    
    requirements_text = "具体需求列表：\n"
    current_length = len(requirements_text)
    
    for i, req in enumerate(requirements_list, 1):
        item_text = f"{i}. {req}\n"
        if current_length + len(item_text) > max_length:
            requirements_text += f"... (共{len(requirements_list)}条需求，已显示前{i-1}条)\n"
            break
        requirements_text += item_text
        current_length += len(item_text)
    
    return requirements_text

# 初始化AI代理
testcase_agent = Agent(model=model, deps_type=TestcaseAgentDeps)


@testcase_agent.system_prompt
async def generate_requirements(ctx: RunContext[TestcaseAgentDeps]) -> str:
    # 获取具体的需求列表
    requirements_list = getattr(ctx.deps, 'requirements_list', [])
    
    # 优化需求内容字符串，避免过长导致超时
    requirements_text = optimize_requirements_text(requirements_list, max_length=800)
    
    return f'''
你是一名高级测试用例生成专家。请根据以下需求和说明，生成高质量的测试用例。

请严格按照以下JSON格式返回测试用例，每个测试用例必须包含8个字段：
[
  {{
    "模块名称": "具体模块名称（如：商品品牌、商品分类、商品管理等）",
    "功能项": "具体功能项（如：列表页、新增、修改、启用、禁用、查询等）",
    "用例说明": "详细的测试用例说明（如：商品品牌页面UI（无数据）、正确新增商品品牌（汉字）等）",
    "前置条件": "执行测试前需要满足的条件（如：正确进入商品品牌页面、列表无数据等）",
    "输入": "测试时需要输入的数据（如：商品品牌名称：迪奥，或者：无）",
    "执行步骤": "具体的操作步骤（如：点击【新增】按钮、查看页面UI等）",
    "预期结果": "期望的测试结果（详细描述预期的系统响应和界面变化）",
    "重要程度": "高/中/低"
  }}
]

测试用例设计要求：
1. 覆盖UI界面验证、功能正确性、输入验证、边界条件、异常处理等
2. 包含正常流程和异常流程的测试场景
3. 每个功能模块要有列表页UI、新增、修改、启用/禁用、查询等功能的测试用例
4. 输入验证要包含：正确输入、为空、超长、重复、特殊字符、边界值等场景
5. 重要程度根据功能重要性和用户影响程度设定

{requirements_text}

用户要求：{ctx.deps.prompt}

请生成详细、专业、可执行的测试用例，确保格式完全符合上述JSON结构。
'''


async def write_test_cases_to_excel(test_cases: List[Dict], file_path: str):
    # 确保测试用例按照标准字段顺序
    standard_columns = ["模块名称", "功能项", "用例说明", "前置条件", "输入", "执行步骤", "预期结果", "重要程度"]
    
    # 重新组织数据，确保字段顺序正确
    standardized_cases = []
    for case in test_cases:
        standardized_case = {}
        for col in standard_columns:
            standardized_case[col] = case.get(col, "")
        standardized_cases.append(standardized_case)
    
    # 将测试用例列表转换为DataFrame，指定列顺序
    df = pd.DataFrame(standardized_cases, columns=standard_columns)

    # 检查文件是否存在
    if os.path.isfile(file_path):
        # 加载现有工作簿
        workbook = load_workbook(file_path)
        # 选择活动工作表
        sheet = workbook.active
        # 将DataFrame追加到现有工作表
        for row in df.itertuples(index=False, name=None):
            sheet.append(row)
        # 保存工作簿
        workbook.save(file_path)
    else:
        # 将DataFrame写入新的Excel文件
        df.to_excel(file_path, index=False, engine='openpyxl')


def is_testcase_output_truncated(test_cases_data, expected_min_count: int = 3) -> bool:
    """
    检测测试用例输出是否被截断
    Args:
        test_cases_data: 测试用例数据
        expected_min_count: 预期最少条数
    Returns:
        是否被截断
    """
    try:
        if isinstance(test_cases_data, str):
            # 处理 markdown 代码块格式
            if test_cases_data.strip().startswith('```json'):
                # 提取 json 内容
                lines = test_cases_data.strip().split('\n')
                json_lines = []
                in_json = False
                for line in lines:
                    if line.strip() == '```json':
                        in_json = True
                        continue
                    elif line.strip() == '```' and in_json:
                        break
                    elif in_json:
                        json_lines.append(line)
                test_cases_data = '\n'.join(json_lines)
            
            # 检查JSON字符串是否完整
            test_cases = json.loads(test_cases_data)
        elif isinstance(test_cases_data, list):
            test_cases = test_cases_data
        else:
            return True
        
        if not test_cases or len(test_cases) == 0:
            return True
        
        # 检查最后一个测试用例是否完整
        last_case = test_cases[-1]
        required_fields = ["模块名称", "功能项", "用例说明", "前置条件", "输入", "执行步骤", "预期结果", "重要程度"]
        
        for field in required_fields:
            if field not in last_case or not last_case[field]:
                return True
        
        return False
        
    except (json.JSONDecodeError, KeyError, IndexError):
        return True


def extract_testcase_data(test_cases_data):
    """
    提取测试用例数据，支持多种格式
    Args:
        test_cases_data: 原始数据
    Returns:
        解析后的测试用例列表
    """
    try:
        if isinstance(test_cases_data, str):
            # 处理 markdown 代码块格式
            if '```json' in test_cases_data:
                # 提取 json 内容
                lines = test_cases_data.split('\n')
                json_lines = []
                in_json = False
                for line in lines:
                    if '```json' in line:
                        in_json = True
                        continue
                    elif line.strip() == '```' and in_json:
                        break
                    elif in_json:
                        # 处理JavaScript风格的注释
                        if '//' in line:
                            line = line.split('//')[0].rstrip()
                        if line.strip():  # 只添加非空行
                            json_lines.append(line)
                
                json_text = '\n'.join(json_lines)
                
                # 尝试修复不完整的JSON
                json_text = json_text.strip()
                if json_text.endswith(','):
                    json_text = json_text[:-1]  # 移除末尾的逗号
                
                # 如果JSON看起来不完整，尝试添加结束括号
                if json_text.count('[') > json_text.count(']'):
                    json_text += ']'
                
                test_cases_data = json_text
            
            # 如果包含其他文本，尝试提取JSON部分
            elif '[' in test_cases_data and ']' in test_cases_data:
                start = test_cases_data.find('[')
                end = test_cases_data.rfind(']') + 1
                test_cases_data = test_cases_data[start:end]
            
            # 清理可能的JavaScript注释
            lines = test_cases_data.split('\n')
            cleaned_lines = []
            for line in lines:
                if '//' in line:
                    line = line.split('//')[0].rstrip()
                if line.strip():
                    cleaned_lines.append(line)
            test_cases_data = '\n'.join(cleaned_lines)
            
            # 尝试修复常见的JSON格式问题
            test_cases_data = fix_json_format(test_cases_data)
            
            test_cases = json.loads(test_cases_data)
        elif isinstance(test_cases_data, list):
            test_cases = test_cases_data
        else:
            test_cases = getattr(test_cases_data, 'data', []) or []
        
        return test_cases
    except Exception as e:
        print(f"解析测试用例数据失败: {e}")
        print(f"原始数据: {test_cases_data[:500]}...")  # 打印前500字符用于调试
        return []


def fix_json_format(json_text):
    """
    修复常见的JSON格式问题
    """
    import re
    
    # 修复不完整的字符串（缺少结束引号）
    lines = json_text.split('\n')
    fixed_lines = []
    
    for line in lines:
        # 检查是否有不完整的字符串值
        if ':' in line and line.count('"') % 2 == 1:
            # 如果引号数量是奇数，可能缺少结束引号
            if line.strip().endswith(',') or line.strip().endswith('}'):
                # 在逗号或大括号前添加引号
                line = re.sub(r'([^"]+)([,}])$', r'\1"\2', line)
            else:
                # 在行末添加引号
                line = line.rstrip() + '"'
        
        fixed_lines.append(line)
    
    json_text = '\n'.join(fixed_lines)
    
    # 修复不完整的对象（缺少结束大括号）
    open_braces = json_text.count('{')
    close_braces = json_text.count('}')
    
    if open_braces > close_braces:
        # 添加缺少的结束大括号
        missing_braces = open_braces - close_braces
        json_text = json_text.rstrip()
        if json_text.endswith(','):
            json_text = json_text[:-1]  # 移除末尾逗号
        json_text += '\n' + '  }' * missing_braces
    
    # 确保数组正确闭合
    if json_text.count('[') > json_text.count(']'):
        json_text += ']'
    
    return json_text


async def run_agent(prompt: str, db_path: str = None, excel_path: str = None, filter: str = None, start_id: int = 1, target_count: int = 25, max_batch_size: int = 15, requirements_list: list = None) -> list:
    """
    运行测试用例生成智能体，支持智能分批和重试机制
    Args:
        prompt: 用户提示
        db_path: 数据库路径
        excel_path: Excel 输出路径
        filter: 过滤条件
        start_id: ID 起始值（用于提示模型当前数据范围）
        target_count: 目标生成数量
        max_batch_size: 单批最大条数（用于分批时）
        requirements_list: 具体需求列表
    Returns:
        生成的测试用例列表
    """
    import time
    start_time = time.time()
    
    # 初始化性能监控
    performance_monitor.start_total_timing()
    
    # 第一次尝试：一次性生成全部
    enhanced_prompt = f"{prompt}，请生成约 {target_count} 条测试用例，确保覆盖所有重要功能点。"
    
    # 使用重试机制包装API调用
    async def first_attempt():
        return await testcase_agent.run(enhanced_prompt, deps=TestcaseAgentDeps(
            db_path=db_path,
            excel_path=excel_path,
            filter=filter,
            prompt=enhanced_prompt,
            total=target_count,
            batch_size=0,  # 不分批
            requirements_list=requirements_list or []  # 传递需求列表
        ))
    
    try:
        result = await retry_with_backoff(first_attempt, max_retries=BATCH_CONFIG["max_retries"], base_delay=BATCH_CONFIG["base_delay"])
        print("testcase_agent.run result:", result)
        print("testcase_agent.run data:", result.data)
        
        # 提取测试用例数据
        test_cases_data = result.data
        test_cases = extract_testcase_data(test_cases_data)
        
        # 检查是否达到目标数量
        if len(test_cases) >= target_count * BATCH_CONFIG["target_completion_ratio"]:  # 使用配置的完成度比例
            elapsed = time.time() - start_time
            print(f"一次性生成完成，共 {len(test_cases)} 条测试用例，耗时 {elapsed:.2f} 秒")
            final_test_cases = test_cases[:target_count]  # 截取到目标数量
            
            # 写入Excel文件
            if excel_path and final_test_cases:
                try:
                    await write_test_cases_to_excel(final_test_cases, excel_path)
                    print(f"测试用例已成功写入Excel文件: {excel_path}")
                except Exception as e:
                    print(f"写入Excel文件失败: {e}")
            
            return final_test_cases
        
        print(f"一次性生成了 {len(test_cases)} 条，未达到目标 {target_count} 条，启动分批模式...")
        
    except Exception as e:
        print(f"第一次尝试失败: {e}")
        print("启动降级模式：使用更简单的提示词重试...")
        
        # 降级策略：使用更简单的提示词
        simple_prompt = f"生成 {min(target_count, 10)} 条商品管理模块的测试用例"
        
        async def fallback_attempt():
            return await testcase_agent.run(simple_prompt, deps=TestcaseAgentDeps(
                db_path=db_path,
                excel_path=excel_path,
                filter=filter,
                prompt=simple_prompt,
                total=min(target_count, 10),
                batch_size=0,
                requirements_list=[]  # 降级时不传递需求列表
            ))
        
        try:
            result = await retry_with_backoff(fallback_attempt, max_retries=BATCH_CONFIG["max_retries"], base_delay=BATCH_CONFIG["base_delay"])
            test_cases_data = result.data
            test_cases = extract_testcase_data(test_cases_data)
            elapsed = time.time() - start_time
            print(f"降级模式成功，生成 {len(test_cases)} 条测试用例，耗时 {elapsed:.2f} 秒")
            
            if excel_path and test_cases:
                try:
                    await write_test_cases_to_excel(test_cases, excel_path)
                    print(f"测试用例已成功写入Excel文件: {excel_path}")
                except Exception as e:
                    print(f"写入Excel文件失败: {e}")
            
            return test_cases
            
        except Exception as fallback_error:
            print(f"降级模式也失败了: {fallback_error}")
            print("返回空列表")
            return []
    
    # 分批处理模式
    all_test_cases = test_cases.copy() if test_cases else []
    batch_num = 2  # 从第2批开始，因为第1批已经生成了
    
    # 累积所有测试用例，最后一次性写入Excel，避免频繁I/O
    while len(all_test_cases) < target_count:
        batch_start_time = time.time()
        remaining = target_count - len(all_test_cases)
        batch_size = min(max_batch_size, remaining)
        
        # 简化批次提示词，避免复杂的上下文累积
        batch_prompt = f"{prompt}，请生成 {batch_size} 条不同的测试用例。"
        
        # 使用重试机制包装批次调用，减少重试次数
        async def batch_attempt():
            return await testcase_agent.run(batch_prompt, deps=TestcaseAgentDeps(
                db_path=db_path,
                excel_path=excel_path,
                filter=filter,
                prompt=batch_prompt,
                total=batch_size,
                batch_size=batch_size,
                requirements_list=requirements_list or []  # 传递需求列表
            ))
        
        try:
            result = await retry_with_backoff(batch_attempt, max_retries=BATCH_CONFIG["max_retries"], base_delay=BATCH_CONFIG["base_delay"])
            test_cases_data = result.data
            batch_test_cases = extract_testcase_data(test_cases_data)
            
            batch_elapsed = time.time() - batch_start_time
            
            if not batch_test_cases:
                print(f"第 {batch_num} 批次无有效测试用例，结束分批")
                break
            
            all_test_cases.extend(batch_test_cases)
            
            print(f"第 {batch_num} 批次完成，生成 {len(batch_test_cases)} 条，累计 {len(all_test_cases)} 条，耗时 {batch_elapsed:.2f} 秒")
            
            # 记录批次性能
            performance_monitor.record_batch(batch_num, len(batch_test_cases), batch_elapsed)
            
            # 如果达到目标数量，结束
            if len(all_test_cases) >= target_count:
                print(f"已达到目标数量 {target_count} 条，结束分批")
                break
            
            batch_num += 1
            
            # 防止无限循环
            if batch_num > BATCH_CONFIG["max_batch_limit"]:  # 使用配置的最大批次限制
                print("达到最大批次限制，结束分批")
                break
                
        except Exception as e:
            print(f"第 {batch_num} 批次失败: {e}，结束分批")
            break
    
    total_elapsed = time.time() - start_time
    print(f"分批模式完成，总共生成 {len(all_test_cases)} 条测试用例，总耗时 {total_elapsed:.2f} 秒")
    
    # 打印性能总结
    print(performance_monitor.get_summary())
    
    final_test_cases = all_test_cases[:target_count]  # 截取到目标数量
    
    # 一次性写入Excel文件，避免频繁I/O
    if excel_path and final_test_cases:
        try:
            await write_test_cases_to_excel(final_test_cases, excel_path)
            print(f"测试用例已成功写入Excel文件: {excel_path}")
        except Exception as e:
            print(f"写入Excel文件失败: {e}")
    
    return final_test_cases

