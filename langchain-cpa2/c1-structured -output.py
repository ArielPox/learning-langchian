from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from typing import Optional,Literal
import os

# 加载 .env 文件中的环境变量
load_dotenv()

# create model obj
model = ChatOpenAI(
    model="qwen-plus",
    api_key=os.getenv("TONGYI_API_KEY"),
    base_url=os.getenv("ALIYUN_BASE_URL"),
)



model_with_openrouter=ChatOpenAI(
    model='qwen-plus',
    api_key=os.getenv('OPENROUTER_API_KEY'),
    base_url=os.getenv('OPENROUTER_BASE_URL')
    
)

# class Person(BaseModel):
#     """人物信息"""
#     name:str=Field(description="name")
#     age:int=Field(description='age')
#     occupation:str=Field(description="occupation")

# structured_model=model.with_structured_output(Person)

# result=structured_model.invoke("andy is a 30 years old engineer")

# print(result)
# print(type(result))

# eg2
class SentimentAnalysis(BaseModel):
    """情感分析结果"""
    sentiment:Optional[str]=Field(default='positive',description="sentiment:positive/negative/neutral")
    confidence:float=Field(default=0.8,description='value between 0-1',ge=0.3,le=0.99)
    keywords:list[str]=Field(description='list of keywords')
    recommend_level:Literal['low','midlle','high']=Field(description='recommend level')

# stuctured_model=model.with_structured_output(SentimentAnalysis)
structured_llm=model_with_openrouter.with_structured_output(SentimentAnalysis)

#invoke
text='i learned LLM develop,i got some knowledge'

result=structured_llm.invoke(
    f'分析下面的文本：\n{text}'
    )

print(f'type:{type(result)}')
print(f'sentiment:{result.sentiment}')
print(f'confidence:{result.confidence}')
print(f"keywords:{result.keywords}")
print(f"recommend_level:{result.recommend_level}")