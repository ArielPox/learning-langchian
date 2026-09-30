# Cap3 Agent 工具、结构化输出与流式输出复习笔记

## 1. @tool(parse_docstring=True)

### 结构

```python
@tool(parse_docstring=True)
def get_weather(city: str):
    """
    天气查询工具

    Args:
        city: 城市名称
    """
    return f"{city}天气晴朗"
```

### 功能

把函数转换成工具，并从 Google 风格 docstring 中解析参数说明。

### 使用步骤

1. 导入 `tool`。
2. 给函数写类型标注。
3. 写规范 docstring。
4. 添加 `@tool(parse_docstring=True)`。
5. 传入 `create_agent(tools=[...])`。

### 注意项

- `parse_docstring=True` 要求 docstring 格式规范。
- 函数名和 docstring 会影响模型选工具。
- 工具参数必须清楚，否则模型容易传错。

### 生产中必须知道的问题

**问题：`parse_docstring=True` 的作用是什么？**

答：让 LangChain 从 docstring 中解析工具描述和参数说明，帮助模型更准确地调用工具。

## 2. create_agent 绑定工具

### 结构

```python
agent = create_agent(
    model=model,
    tools=[get_weather],
    name="weather_agent",
)
```

### 功能

创建一个可以根据用户问题自动调用工具的 Agent。

### 使用步骤

1. 初始化模型。
2. 定义工具。
3. 调用 `create_agent`。
4. 用 `agent.invoke({"messages": [...]})` 执行。

### 注意项

- `system` 消息可以写在 `messages` 中，也可以用 `system_prompt` 参数。
- Agent 返回完整消息列表，可通过 `pretty_print()` 查看工具调用过程。
- 工具名拼写要注意，代码中 `get_wether` 建议改成 `get_weather`。

### 生产中必须知道的问题

**问题：Agent 是怎么决定调用哪个工具的？**

答：模型会根据用户输入、工具名、参数 Schema 和工具描述判断是否需要调用工具以及调用哪个工具。

## 3. 内置工具 TavilySearch

### 结构

```python
from langchain_tavily import TavilySearch

web_search = TavilySearch(max_results=2)

agent = create_agent(
    model=model,
    tools=[web_search],
    system_prompt="你是信息检索助手",
)
```

### 功能

给 Agent 增加联网搜索能力，适合查询实时信息或外部资料。

### 使用步骤

1. 安装并导入 `langchain_tavily`。
2. 配置 `TAVILY_API_KEY`。
3. 创建 `TavilySearch` 工具。
4. 交给 Agent 使用。

### 注意项

- 搜索工具依赖网络和 API Key。
- 查询最新信息时应使用搜索工具，不要只依赖模型记忆。
- 搜索结果需要模型再总结，不能直接等同最终答案。

### 生产中必须知道的问题

**问题：什么时候需要 TavilySearch 这类工具？**

答：当问题涉及实时信息、外部资料、模型知识可能过期时，需要搜索工具。

## 4. Agent 结构化输出 ToolStrategy

### 结构

```python
from langchain.agents.structured_output import ToolStrategy

class ContactInfo(BaseModel):
    name: str = Field(description="姓名")
    email: str = Field(description="邮箱")
    phone: str = Field(description="手机号")

agent = create_agent(
    model=model,
    response_format=ToolStrategy(ContactInfo),
)
```

### 功能

让 Agent 最终返回符合指定 Schema 的结构化结果。

### 使用步骤

1. 定义 Pydantic Schema。
2. 导入 `ToolStrategy`。
3. 在 `create_agent` 中设置 `response_format`。
4. 调用 Agent。
5. 从 `result["structured_response"]` 读取对象。

### 注意项

- `ToolStrategy` 会通过类似工具调用的方式生成结构化结果。
- 适合抽取联系信息、分析报告、分类结果。
- 结构化输出和普通工具调用可以同时使用。

### 生产中必须知道的问题

**问题：`response_format=ToolStrategy(...)` 解决什么问题？**

答：它让 Agent 的最终答案变成结构化对象，而不是不可控的自然语言文本。

## 5. ToolStrategy 参数

### 结构

```python
ToolStrategy(
    ContactInfo,
    tool_message_content="结构化输出已生成",
    handle_errors="默认错误处理",
)
```

### 功能

控制结构化输出过程中的工具消息内容和错误处理策略。

### 使用步骤

1. 第一个参数传入目标 Schema。
2. 用 `tool_message_content` 替换默认 ToolMessage 内容。
3. 用 `handle_errors` 控制校验失败时如何处理。

### 注意项

- `tool_message_content` 可以减少上下文 token。
- 它影响的是消息历史中的伪 ToolMessage，不是最终结构化对象。
- 错误处理要结合业务场景设置。

### 生产中必须知道的问题

**问题：`tool_message_content` 有什么作用？**

答：它替换结构化输出成功后插入消息历史的 ToolMessage 内容，减少 token 消耗并改善展示。

## 6. Agent 流式输出

### 结构

```python
for chunk in agent.stream(
    {"messages": [HumanMessage("抽取联系信息...")]},
    stream_mode="custom",
):
    print(chunk)
```

### 功能

实时观察 Agent 执行过程，改善长任务体验。

### 使用步骤

1. 创建 Agent。
2. 调用 `agent.stream(...)`。
3. 设置 `stream_mode`。
4. 遍历 chunk。

### 注意项

- 常见模式有 `updates`、`values`、`messages`、`custom`、`tasks`、`debug`。
- 不同模式输出内容不同。
- 流式输出适合长任务、工具调用、调试 Agent 执行过程。

### 生产中必须知道的问题

**问题：为什么要用流式输出？**

答：Agent 可能经历多轮模型和工具调用，流式输出可以实时展示进度，避免用户长时间无反馈。

## 7. 多功能助手封装

### 结构

```python
class MultiFuncAssistant:
    def __init__(self):
        self.tools = [...]
        self.agent = create_agent(
            model=model,
            tools=self.tools,
            system_prompt=system_prompt,
        )
        self.message = []

    def chat(self, user_input: str) -> str:
        self.message.append({"role": "user", "content": user_input})
        result = self.agent.invoke({"messages": self.message})
        self.message = result["messages"]
        return result["messages"][-1].content
```

### 功能

把多工具 Agent 封装成可复用的对话助手类。

### 使用步骤

1. 定义多个工具函数。
2. 在类初始化时创建 Agent。
3. 用列表维护消息历史。
4. 提供 `chat()` 方法。
5. 提供 `reset()` 方法清空上下文。

### 注意项

- `eval(expression)` 有安全风险，真实项目不要直接执行用户输入。
- 手动维护 `self.message` 适合教学，生产中可考虑 checkpointer。
- 工具描述和系统提示词要保持一致。

### 生产中必须知道的问题

**问题：多功能助手为什么要维护 `self.message`？**

答：为了保留对话历史，让下一轮调用时模型能看到前面的上下文。

## 综合练习

### 结构

构建一个多功能学习助手，包含：

- 天气工具
- 数学计算工具
- 信息搜索工具
- 联系信息结构化抽取
- 流式输出

### 功能

练习工具调用、结构化输出、流式观察和类封装。

### 使用步骤

1. 定义三个工具。
2. 定义一个 `ContactInfo` Schema。
3. 创建 Agent。
4. 分别用 `invoke` 和 `stream` 调用。
5. 打印完整消息和最终答案。

### 注意项

- 工具能力与结构化输出是两个不同层面。
- 复杂任务先看完整消息，确认工具是否被调用。
- 涉及外部搜索时要处理 API Key 缺失场景。

### 生产中必须知道的问题

**问题：Agent 调用工具和结构化输出会不会冲突？**

答：不会。工具调用用于完成任务，结构化输出用于约束最终结果格式，两者可以组合。
