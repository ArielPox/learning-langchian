# Cap1 LangChain 基础能力复习笔记

## 1. 环境变量与模型初始化

### 结构

```python
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

model = ChatOpenAI(
    model="qwen-plus",
    api_key=os.getenv("TONGYI_API_KEY"),
    base_url=os.getenv("ALIYUN_BASE_URL"),
)
```

### 功能

通过 `.env` 管理 API Key、模型服务地址等敏感配置，再创建可调用的大模型对象。

### 使用步骤

1. 在 `.env` 中配置 `TONGYI_API_KEY` 和 `ALIYUN_BASE_URL`。
2. 使用 `load_dotenv()` 加载环境变量。
3. 用 `ChatOpenAI` 或 `init_chat_model` 创建模型对象。
4. 使用 `model.invoke(...)` 调用模型。

### 注意项

- 不要把 API Key 写死在代码里。
- 项目中同时出现了 `ALIYUN-BASE-URL` 和 `ALIYUN_BASE_URL`，建议统一使用下划线版本。
- `ChatOpenAI` 可以接入兼容 OpenAI 协议的模型服务。

### 生产中必须知道的问题

**问题：为什么要用 `.env` 管理 API Key？**

答：API Key 属于敏感信息，放在 `.env` 中可以避免硬编码到代码里，便于不同环境切换，也降低泄露风险。

## 2. 直接调用模型

### 结构

```python
response = model.invoke("你是谁？")
print(response.content)
```

### 功能

直接把用户文本交给模型，得到一个 `AIMessage`，再读取 `content` 获取回答正文。

### 使用步骤

1. 创建模型对象。
2. 调用 `model.invoke("问题")`。
3. 读取 `response.content`。

### 注意项

- `invoke()` 返回的不是普通字符串，而是消息对象。
- 如果只想看正文，读取 `.content`。
- 如果要调试完整消息，可使用 `pretty_print()`。

### 生产中必须知道的问题

**问题：`model.invoke()` 返回什么？**

答：通常返回一个 `AIMessage` 对象，正文在 `response.content` 中。

## 3. Agent 中使用模型和工具

### 结构

```python
from langchain.agents import create_agent
from langchain.tools import tool

@tool
def get_weather(city: str) -> str:
    """查询指定城市天气。"""
    return f"{city}今天晴"

agent = create_agent(
    model=model,
    tools=[get_weather],
    system_prompt="天气问题必须使用 get_weather 工具。",
)
```

### 功能

Agent 可以让模型自主判断是否需要调用工具，再根据工具结果生成最终回答。

### 使用步骤

1. 用 `@tool` 定义工具。
2. 用 `create_agent` 创建智能体。
3. 把模型、工具和系统提示词传给 Agent。
4. 通过 `agent.invoke({"messages": [...]})` 提问。

### 注意项

- 工具描述越清晰，模型越容易正确选择工具。
- `system_prompt` 可以明确要求某类问题必须调用工具。
- Agent 的返回值通常包含完整消息列表，不只是最终文本。

### 生产中必须知道的问题

**问题：模型和 Agent 的区别是什么？**

答：模型只负责生成文本或工具调用意图；Agent 负责组织模型、工具和状态，让模型可以多步执行任务。

## 4. LangChain 消息对象

### 结构

```python
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

messages = [
    SystemMessage(content="你是 Python 老师"),
    HumanMessage(content="解释变量"),
    AIMessage(content="变量是保存数据的名字"),
    HumanMessage(content="再举例"),
]

response = model.invoke(messages)
```

### 功能

用消息对象明确区分系统消息、用户消息和模型消息，构造多轮对话上下文。

### 使用步骤

1. 用 `SystemMessage` 设置模型角色。
2. 用 `HumanMessage` 表示用户输入。
3. 用 `AIMessage` 表示历史模型回复。
4. 把消息列表传给 `model.invoke()`。

### 注意项

- 多轮对话本质上就是传入历史消息列表。
- `SystemMessage` 通常放在最前面。
- 历史消息过多会消耗更多 token。

### 生产中必须知道的问题

**问题：`SystemMessage`、`HumanMessage`、`AIMessage` 分别是什么？**

答：`SystemMessage` 设置角色和规则，`HumanMessage` 表示用户输入，`AIMessage` 表示模型历史回复。

## 5. 多模态消息

### 结构

```python
message = HumanMessage(
    content_blocks=[
        {"type": "text", "text": "一句话描述图片"},
        {
            "type": "image",
            "base64": local_image_to_data_url("test.png"),
            "mime_type": "image/png",
        },
    ]
)

response = model.invoke([message])
```

### 功能

让模型同时接收文本和图片，用于图片描述、OCR、图像理解等任务。

### 使用步骤

1. 读取本地图片并转成 base64。
2. 创建 `HumanMessage`。
3. 在 `content_blocks` 中放入文本块和图片块。
4. 调用支持视觉能力的模型。

### 注意项

- 必须使用支持图片理解的模型。
- 图片需要提供正确的 `mime_type`。
- 大图片会增加请求体积和成本。

### 生产中必须知道的问题

**问题：多模态消息和普通消息有什么区别？**

答：普通消息通常只有文本内容；多模态消息可以包含文本、图片等多个内容块。

## 6. 提示词工程与 ChatPromptTemplate

### 结构

```python
from langchain_core.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate.from_messages([
    ("system", "你是 Python 老师，用中文回答。"),
    ("human", "请讲解这个概念：{concept}"),
])

messages = prompt.invoke({"concept": "装饰器"})
response = model.invoke(messages)
```

### 功能

把提示词模板化，清晰区分角色、任务、约束和变量。

### 使用步骤

1. 使用 `ChatPromptTemplate.from_messages` 定义模板。
2. 在模板中使用 `{变量名}`。
3. 调用 `prompt.invoke({...})` 填充变量。
4. 把生成的消息交给模型。

### 注意项

- 好提示词通常包含角色、任务、背景、约束、输出格式。
- 提示词格式约束不是强校验，模型仍可能偏离。
- 如果需要强结构，应该使用结构化输出。

### 生产中必须知道的问题

**问题：为什么要使用 `ChatPromptTemplate`？**

答：它可以把提示词工程化，便于复用、变量填充和区分 system/human 消息。

## 7. 模型结构化输出

### 结构

```python
from pydantic import BaseModel, Field

class ConceptExplanation(BaseModel):
    concept: str = Field(description="概念解释")
    analogy: str = Field(description="生活类比")
    code_example: str = Field(description="代码示例")
    common_mistake: str = Field(description="常见误区")

structured_model = model.with_structured_output(
    ConceptExplanation,
    method="function_calling",
)
```

### 功能

让模型输出被解析成 Pydantic 对象，后续代码可以直接读取字段。

### 使用步骤

1. 定义 Pydantic Schema。
2. 调用 `model.with_structured_output(Schema)`。
3. 使用结构化模型调用。
4. 通过字段读取结果。

### 注意项

- 字段描述会影响模型填充质量。
- 结构化输出适合抽取、分类、格式化生成。
- 输出失败时需要考虑重试或错误处理。

### 生产中必须知道的问题

**问题：结构化输出相比普通文本有什么优势？**

答：结构化输出可以让结果变成可验证、可读取的对象，适合程序继续处理。

## 8. 自定义工具

### 结构

```python
@tool
def add_numbers(a: int, b: int) -> int:
    """计算两个整数的和。"""
    return a + b

print(add_numbers.invoke({"a": 1, "b": 2}))
```

### 功能

把普通 Python 函数包装成模型可以调用的 LangChain Tool。

### 使用步骤

1. 编写普通函数。
2. 添加类型标注。
3. 写清楚 docstring。
4. 使用 `@tool` 装饰。
5. 可以单独 `.invoke()` 测试，也可以交给 Agent。

### 注意项

- 函数名、参数类型、docstring 都会影响模型选择工具。
- 工具可以脱离 Agent 单独测试。
- 工具中不要执行不安全操作，除非有审批或沙箱。

### 生产中必须知道的问题

**问题：定义工具时最重要的三点是什么？**

答：函数名、参数类型、docstring。它们共同告诉模型工具能做什么、需要什么参数、什么时候使用。

## 9. 预定义工具与工具包装

### 结构

```python
from langchain_tavily import TavilySearch

tavily_search = TavilySearch(max_results=3)

@tool
def search_web_with_tavily(query: str) -> str:
    """使用 Tavily 搜索网络信息。"""
    return tavily_search.invoke({"query": query})
```

### 功能

使用 LangChain 或第三方已经封装好的工具，并根据业务需要再包装一层。

### 使用步骤

1. 创建预定义工具对象。
2. 如有需要，用 `@tool` 包装成业务工具。
3. 统一工具返回格式。
4. 交给 Agent 使用。

### 注意项

- 外部工具通常需要额外 API Key。
- 包装工具可以统一返回格式，也可以加入业务规则。
- 搜索类工具适合处理最新信息或外部资料问题。

### 生产中必须知道的问题

**问题：为什么要把预定义工具再包装一层？**

答：可以统一输入输出格式、隐藏第三方细节、加入业务规则，让 Agent 使用更稳定。

## 10. 短期记忆 checkpointer

### 结构

```python
from langgraph.checkpoint.memory import InMemorySaver

memory = InMemorySaver()

agent = create_agent(
    model=model,
    tools=[],
    checkpointer=memory,
)

config = {"configurable": {"thread_id": "study-sinda"}}
agent.invoke({"messages": [...]}, config=config)
```

### 功能

让 Agent 在同一个 `thread_id` 下记住历史对话。

### 使用步骤

1. 创建 `InMemorySaver()`。
2. 在 `create_agent` 中传入 `checkpointer`。
3. 调用 Agent 时传入 `configurable.thread_id`。
4. 相同 `thread_id` 共享短期记忆。

### 注意项

- `InMemorySaver` 只保存在内存中，程序结束后消失。
- 不同 `thread_id` 的会话互不影响。
- 生产环境通常需要持久化 checkpointer。

### 生产中必须知道的问题

**问题：`thread_id` 的作用是什么？**

答：用于区分不同会话。同一个 `thread_id` 会继承历史消息，不同 `thread_id` 互不影响。

## 综合练习

### 结构

创建一个“学习助手 Agent”，具备：

- 模型初始化
- 提示词模板
- 天气工具
- 加法工具
- 短期记忆

### 功能

用户可以连续提问，Agent 能记住同一会话中的姓名和学习主题，并在需要时调用工具。

### 使用步骤

1. 定义 `get_weather` 和 `add_numbers`。
2. 创建 `InMemorySaver`。
3. 创建 Agent。
4. 用同一个 `thread_id` 连续问两次。
5. 换一个 `thread_id` 验证记忆隔离。

### 注意项

- 工具逻辑放在 Tool。
- 对话记忆交给 checkpointer。
- 角色和回答风格写在 `system_prompt`。

### 生产中必须知道的问题

**问题：Tool、Prompt、Memory 分别解决什么问题？**

答：Tool 提供外部能力，Prompt 约束模型行为，Memory 保存会话历史。
