import os

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.structured_output import ToolStrategy
from langchain.chat_models import init_chat_model
from langchain.messages import HumanMessage
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


# padantic way to define structure output
class ContactInfo(BaseModel):
    """用户的联系方式"""

    name: str = Field(description="用户姓名")
    email: str = Field(description="用户邮箱地址")
    phone: str = Field(description="用户的手机号")


# init agent
agent = create_agent(model=model, response_format=ToolStrategy(ContactInfo))

# invoke agent
rep = agent.invoke(
    {
        "messages": [
            HumanMessage(
                "从这段话中抽取结构化信息：小明的邮箱地址为：shkstart@atguigu.com，手机号：12345678912"
            )
        ]
    }
)

for msg in rep["messages"]:
    msg.pretty_print()
