import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

# 第一步：加载 .env 文件中的环境变量。
load_dotenv()

# 第二步：创建模型对象。
# 通义千问提供了兼容 OpenAI 的接口，因此可以使用 ChatOpenAI。
model = ChatOpenAI(
    model="qwen3.6-plus",
    api_key=os.getenv("TONGYI_API_KEY"),
    base_url=os.getenv("ALIYUN-BASE-URL"),
)

# 第三步：调用模型。
# invoke() 接收用户问题，返回一个 AIMessage 对象。
response = model.invoke("你是谁？")

# 第四步：输出模型回复的正文。
print(response.content)
