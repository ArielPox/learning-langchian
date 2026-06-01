import os

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

# LangChain 中常用的消息类型：
# SystemMessage：系统消息，用于设定模型的行为。
# HumanMessage：用户消息，表示用户提出的问题。
# AIMessage：模型回复。调用模型后，返回值就是一个 AIMessage 对象。

# 第一步：加载 .env 文件中的环境变量。
load_dotenv()

# 第二步：创建模型对象。
model = ChatOpenAI(
    model="qwen3.6-plus",
    api_key=os.getenv("TONGYI_API_KEY"),
    base_url=os.getenv("ALIYUN-BASE-URL"),
)

# 第三步：使用消息对象组织对话。
messages = [
    SystemMessage(content="你是一名耐心的 Python 老师。"),
    HumanMessage(content="请用一句话解释什么是变量。"),
    AIMessage(content='nice to meet you'),
    HumanMessage(content='who are you?'),
]

# 第四步：将消息列表发送给模型。
response = model.invoke(messages)

# 第五步：查看发送给模型的消息和模型返回的消息。
for message in messages:
    message.pretty_print()

response.pretty_print()
