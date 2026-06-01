from dotenv import load_dotenv
import os

from openai import OpenAI

load_dotenv()


api_key = os.getenv("TONGYI_API_KEY")

# 创建客户端
client = OpenAI(
    api_key=api_key,
    base_url=os.getenv("BASE-URL"),
)

completion = client.chat.completions.create(
    model="qwen3.6-plus",
    messages=[
        {
            'role':'system',
            'content':'you are a guide'
        },
        {
            'role':'user',
            'content':'今天南京天气如何?'
        },
    ]
)

print(completion.model_dump_json(indent=2))
