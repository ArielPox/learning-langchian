import os

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_openai import ChatOpenAI
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


model_with_openrouter = ChatOpenAI(
    model="qwen-plus",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url=os.getenv("OPENROUTER_BASE_URL"),
)


class Person(BaseModel):
    """人物信息"""

    name: str = Field(description="name")
    age: int = Field(description="age")
    occupation: str = Field(description="occupation")


class PersonList(BaseModel):
    """people list"""

    community: str = (Field(description="angel community"),)
    # 嵌套结构
    people: list[Person]


structured_model = model.with_structured_output(PersonList, include_raw=True)

result = structured_model.invoke(
    "in happy house,andy is a 30 years old engineer,and tom can cook"
)

rprint(result)
