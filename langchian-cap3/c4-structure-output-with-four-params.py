import os

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.structured_output import ToolStrategy
from langchain.chat_models import init_chat_model
from pydantic import BaseModel, Field

# 加载 .env 文件中的环境变量
load_dotenv()

# create model obj
model = init_chat_model(
    model="qwen-plus",
    model_provider="openai",
    api_key=os.getenv("TONGYI_API_KEY"),
    base_url=os.getenv("ALIYUN_BASE_URL"),
)


class ContactInfo(BaseModel):
    """user`s contact methods"""

    name: str = Field(description="username")
    email: str = Field(description="user address")
    phone: str = Field(description="userphone")


# ToolStrategy的参数列表schema-目标输出结构
# tool_massage_content:> ToolStrategy 会在消息历史插入一条**伪 ToolMessage**（没有真实执行工具，仅用于补全对话上下文）。
# - 默认：填入完整结构化 json 数据，会消耗大量 token；
# - 设置字符串：替换这条 ToolMessage 的内容，减少上下文 token，同时对前端展示更友好。
# handle_errors:校验结构化输出失败时的错误处理策略


agent = create_agent(
    model=model,
    response_format=ToolStrategy(
        ContactInfo,
        tool_message_content="this content will replace ToolMessage,reduce token consume",
        handle_errors="默认",
    ),
)
