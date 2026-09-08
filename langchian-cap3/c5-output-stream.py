import os

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.structured_output import ToolStrategy
from langchain.chat_models import init_chat_model
from langchain.messages import HumanMessage
from pydantic import BaseModel, Field
from rich import print as rprint

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

# stream style output
# message:实时对话交互；updates:思考与执行步骤；values/tasks/debug查看每一步的状态，custom:输出自定义业务
for chunk in agent.stream(
    {
        "messages": [
            HumanMessage(
                "从这段话中抽取结构化信息：小明的邮箱地址为：shkstart@atguigu.com，手机号：12345678912"
            )
        ]
    },
    stream_mode="custom",
):
    rprint(chunk)
    print("-" * 50)
