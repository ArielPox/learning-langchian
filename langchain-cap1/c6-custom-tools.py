import os

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.tools import tool
from langchain_openai import ChatOpenAI

# 自定义工具：把 Python 函数包装成模型可以调用的工具。
#
# 工具的三个关键点：
# 1. 函数名：告诉模型这个工具大概能做什么。
# 2. 参数类型：告诉模型调用工具时需要传入什么。
# 3. 文档字符串：告诉模型什么时候应该使用这个工具。

# 第一步：加载 .env 文件中的环境变量。
load_dotenv()


# 第二步：定义一个天气查询工具。
# @tool 会把普通 Python 函数转换成 LangChain Tool。
@tool
def get_weather(city: str) -> str:
    """查询指定城市的天气。"""
    return f"{city}今天晴，气温 25 摄氏度。这是教学用的模拟数据。"


# 第三步：定义一个加法工具。
@tool
def add_numbers(a: int, b: int) -> int:
    """计算两个整数的和。"""
    return a + b


# 第四步：单独调用工具。
# 注意：这一步不需要模型参与，只是在测试工具函数是否可用。
print("========== 单独调用工具 ==========")
print(get_weather.invoke({"city": "南京"}))
print(add_numbers.invoke({"a": 12, "b": 30}))

# 第五步：创建模型对象。
model = ChatOpenAI(
    model="qwen3.6-plus",
    api_key=os.getenv("TONGYI_API_KEY"),
    base_url=os.getenv("ALIYUN_BASE_URL"),
)

# 第六步：创建智能体，把工具交给智能体。
# 智能体会根据用户问题，自动判断是否需要调用工具。
agent = create_agent(
    model=model,
    tools=[get_weather, add_numbers],
    system_prompt="你是一个助手。需要查询天气或计算加法时，必须使用工具。",
)

# 第七步：向智能体提问。
response = agent.invoke(
    {
        "messages": [
            {
                "role": "user",
                "content": "南京今天的天气怎么样？另外帮我计算 12 加 30 等于多少。",
            }
        ]
    }
)

# 第八步：查看完整消息。
# 这里会看到：用户消息、模型工具调用、工具返回结果、模型最终回答。
print("\n========== 智能体完整消息 ==========")
for message in response["messages"]:
    message.pretty_print()

# 第九步：只输出最终回答。
print("\n========== 最终回答 ==========")
print(response["messages"][-1].content)
