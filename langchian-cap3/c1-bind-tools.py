import os

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain.tools import tool

# 加载 .env 文件中的环境变量
load_dotenv()

# create model obj
model = init_chat_model(
    model="qwen-plus",
    model_provider="openai",
    api_key=os.getenv("TONGYI_API_KEY"),
    base_url=os.getenv("ALIYUN_BASE_URL"),
)


# 定义工具
@tool(parse_docstring=True)
def get_wether(city: str):
    """
    天气查询工具

    Args:
        city:城市名称
    """
    return f"{city}的天气晴朗。25摄氏度"


# 创建agent调用工具
agent = create_agent(model=model, tools=[get_wether], name="agentSubname")


# 模型调用
resp = agent.invoke(
    {
        "messages": [
            {
                "role": "system",
                "content": "你是一个天气查询助手，只回答天气相关的问题，其他问题请直接回答：我不清楚这问题答案。",
            },
            {"role": "user", "content": "南京天气如何?"},
        ]
    }
)

for message in resp["messages"]:
    message.pretty_print()
