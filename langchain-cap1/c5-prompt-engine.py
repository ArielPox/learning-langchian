import os

from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field


class ConceptExplanation(BaseModel):
    """模型需要返回的结构化结果。"""

    concept: str = Field(description="概念解释")
    analogy: str = Field(description="生活类比")
    code_example: str = Field(description="代码示例")
    common_mistake: str = Field(description="常见误区")

# 提示词工程：不是简单地“问一句话”，而是把任务讲清楚。
#
# 一个好的提示词通常包含：
# 1. 角色：让模型知道自己应该以什么身份回答。
# 2. 任务：让模型知道要完成什么事情。
# 3. 背景：告诉模型必要的上下文。
# 4. 约束：限制回答范围、长度、风格。
# 5. 输出格式：让模型按指定结构返回内容。

# 第一步：加载 .env 文件中的环境变量。
load_dotenv()

# 第二步：创建模型对象。
model = ChatOpenAI(
    model="qwen-plus",
    api_key=os.getenv("TONGYI_API_KEY"),
    base_url=os.getenv("ALIYUN_BASE_URL"),
)

# 第三步：普通提示词。
# 这种写法可以运行，但是要求不够明确，模型输出容易发散。
simple_prompt = "解释一下 Python 装饰器。"

# 第四步：工程化提示词。
# 使用 ChatPromptTemplate 可以把提示词拆成 system 和 human 两部分。
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
你是一名 Python 课程老师。
你的目标是让零基础学生也能听懂。

回答要求：
1. 使用中文。
2. 不要使用太多术语。
3. 每个部分不超过 2 句话。
4. 按指定格式输出。
""",
        ),
        (
            "human",
            """
请讲解这个概念：{concept}

输出格式：
概念：
类比：
代码示例：
常见误区：
""",
        ),
    ]
)

# 第五步：把变量填入提示词模板。
messages = prompt.invoke({"concept": "Python 装饰器"})

# 第六步：观察最终发给模型的消息。
print("========== 普通提示词 ==========")
print(simple_prompt)

print("\n========== 工程化提示词 ==========")
for message in messages.to_messages():
    message.pretty_print()

# 第七步：调用模型。
response = model.invoke(messages)

# 第八步：输出模型回复。
print("\n========== 模型回复 ==========")
print(response.content)

# 第九步：结构化输出。
# 上面的“输出格式”只是提示模型按文本格式回答。
# 结构化输出会把模型结果解析成 Python 对象，后续代码可以直接读取字段。
structured_model = model.with_structured_output(
    ConceptExplanation,
    method="function_calling",
)

structured_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
你是一名 Python 课程老师。
请严格返回 JSON，不要输出 Markdown，不要输出多余解释。
JSON 必须包含这些字段：
concept、analogy、code_example、common_mistake。
""",
        ),
        (
            "human",
            "请讲解这个概念：{concept}",
        ),
    ]
)

structured_messages = structured_prompt.invoke({"concept": "Python 装饰器"})
structured_response = structured_model.invoke(structured_messages)

print("\n========== 结构化输出 ==========")
print(structured_response.model_dump_json(indent=2))

print("\n========== 读取结构化字段 ==========")
print(structured_response.concept)
print(structured_response.code_example)
