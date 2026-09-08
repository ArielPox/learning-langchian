import os

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model

# langchain的内置工具，用于联网搜索
from langchain_tavily import TavilySearch

# 加载 .env 文件中的环境变量
load_dotenv()

# create model obj
model = init_chat_model(
    model="qwen-plus",
    model_provider="openai",
    api_key=os.getenv("TONGYI_API_KEY"),
    base_url=os.getenv("ALIYUN_BASE_URL"),
)

# tool
web_search = TavilySearch(max_results=2)

# create agent with connect web ability
agent = create_agent(
    model=model, tools=[web_search], system_prompt="你是信息检索助手，返回内容尽量精简"
)

result = agent.invoke(
    {
        "messages": [
            {"role": "user", "content": "请帮我查询2024年诺贝尔物理学奖得主是谁？"}
        ]
    }
)
for message in result["messages"]:
    message.pretty_print()
