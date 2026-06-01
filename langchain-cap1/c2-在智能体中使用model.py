import os

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.tools import tool
from langchain_openai import ChatOpenAI

# 第一步：加载 .env 文件中的环境变量。
load_dotenv()


# 第二步：定义智能体可以使用的工具。
# 这里返回的是模拟数据，方便观察智能体调用工具的过程。
@tool
def get_weather(city: str) -> str:
    """查询指定城市的天气。"""
    return f"{city}今天晴"


# 第三步：创建模型对象。
model = ChatOpenAI(
    model="qwen3.6-plus",
    api_key=os.getenv("TONGYI_API_KEY"),
    base_url=os.getenv("ALIYUN-BASE-URL"),
)

# 第四步：创建智能体，将模型和工具交给智能体管理。
agent = create_agent(
    model=model,
    tools=[get_weather],
    system_prompt="你是一名助手。回答天气问题时，必须使用 get_weather 工具。",
)

# 第五步：向智能体提问。
# 智能体会先调用模型，由模型判断是否需要使用工具，然后生成最终回答。
response = agent.invoke(
    {
        "messages": [
            {
                "role": "user",
                "content": "今天南京的天气如何？",
            }
        ]
    }
)

# 第六步：输出智能体给出的最终回答。
print(response)
