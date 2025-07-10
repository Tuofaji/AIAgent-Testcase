from pydantic_ai.models.openai import OpenAIModel
import httpx
import asyncio
from typing import Optional

# 创建带有超时配置的HTTP客户端
http_client = httpx.AsyncClient(
    timeout=httpx.Timeout(200.0),
    limits=httpx.Limits(max_connections=10, max_keepalive_connections=2)
)

model = OpenAIModel(
    model_name="qwen-max",
    api_key="your api key",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    http_client=http_client
)

