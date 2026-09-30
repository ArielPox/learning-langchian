# Cap2 结构化输出复习笔记

## 1. with_structured_output 基础用法

### 结构

```python
from pydantic import BaseModel, Field

class Person(BaseModel):
    name: str = Field(description="姓名")
    age: int = Field(description="年龄")
    occupation: str = Field(description="职业")

structured_model = model.with_structured_output(Person)
result = structured_model.invoke("Andy is a 30 years old engineer")
```

### 功能

把模型输出转换为符合 Pydantic Schema 的 Python 对象。

### 使用步骤

1. 定义继承 `BaseModel` 的数据结构。
2. 用 `Field(description=...)` 描述字段含义。
3. 调用 `model.with_structured_output(Schema)`。
4. 使用结构化模型进行 `invoke`。

### 注意项

- Schema 字段越清楚，抽取效果越稳定。
- 类型会约束模型输出，例如 `int`、`float`、`list[str]`。
- 结构化输出不是普通字符串，结果可以直接访问字段。

### 生产中必须知道的问题

**问题：为什么结构化输出常配合 Pydantic？**

答：Pydantic 可以定义字段、类型、默认值和校验规则，让模型输出变成可验证的数据对象。

## 2. Field 默认值与校验

### 结构

```python
from typing import Literal

class SentimentAnalysis(BaseModel):
    sentiment: str | None = Field(default="positive")
    confidence: float = Field(default=0.8, ge=0.3, le=0.99)
    keywords: list[str] = Field(description="关键词列表")
    recommend_level: Literal["low", "middle", "high"]
```

### 功能

通过字段类型、默认值、取值范围和枚举限制，提高输出质量。

### 使用步骤

1. 用 `default` 设置默认值。
2. 用 `ge`、`le` 限制数值范围。
3. 用 `Literal` 限制枚举取值。
4. 用列表类型抽取多个信息。

### 注意项

- 枚举值拼写要准确，代码中 `midlle` 建议改成 `middle`。
- 范围约束可以减少不合理结果。
- 字段默认值不等于模型一定会使用默认值。

### 生产中必须知道的问题

**问题：`Literal` 在结构化输出里有什么用？**

答：限制字段只能从指定选项中取值，常用于分类、等级、状态等场景。

## 3. 多模型服务配置

### 结构

```python
model = init_chat_model(
    model="qwen-plus",
    model_provider="openai",
    api_key=os.getenv("TONGYI_API_KEY"),
    base_url=os.getenv("ALIYUN_BASE_URL"),
)

model_with_openrouter = init_chat_model(
    model="qwen-plus",
    model_provider="openai",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url=os.getenv("OPENROUTER_BASE_URL"),
)
```

### 功能

通过不同 API Key 和 Base URL 接入不同模型服务商。

### 使用步骤

1. 在 `.env` 中配置不同服务商的 Key。
2. 分别初始化模型对象。
3. 给需要的模型调用 `with_structured_output`。

### 注意项

- 不同服务商对结构化输出支持能力可能不同。
- Base URL 与 API Key 要配套。
- 调试时先确认普通 `invoke` 可用，再测试结构化输出。

### 生产中必须知道的问题

**问题：同一个 LangChain 项目能接多个模型服务吗？**

答：可以。只要服务兼容对应接口，就可以通过不同 `api_key` 和 `base_url` 初始化多个模型对象。

## 4. 嵌套结构与列表抽取

### 结构

```python
class Person(BaseModel):
    name: str = Field(description="姓名")
    age: int = Field(description="年龄")
    occupation: str = Field(description="职业")

class PersonList(BaseModel):
    community: str = Field(description="社区名称")
    people: list[Person]

structured_model = model.with_structured_output(PersonList)
```

### 功能

从一段文本中抽取多个对象，并放入嵌套列表结构。

### 使用步骤

1. 先定义单个对象 Schema。
2. 再定义包含 `list[对象]` 的外层 Schema。
3. 调用结构化模型抽取文本。

### 注意项

- 嵌套结构要避免字段歧义。
- 如果文本中某些字段缺失，模型可能补全或报错。
- 代码中 `community: str = (Field(...),)` 多了逗号，会让字段变成元组，建议改为 `community: str = Field(...)`。

### 生产中必须知道的问题

**问题：如何抽取多个人的信息？**

答：定义单个人的 Schema，再定义外层列表 Schema，例如 `people: list[Person]`。

## 5. include_raw 参数

### 结构

```python
structured_model = model.with_structured_output(
    PersonList,
    include_raw=True,
)
```

### 功能

同时返回原始模型消息、解析后的结构化结果、解析错误信息。

### 使用步骤

1. 调用 `with_structured_output(..., include_raw=True)`。
2. 执行 `invoke`。
3. 查看返回字典中的原始消息和解析结果。

### 注意项

- `include_raw=True` 适合调试。
- 生产环境如果只需要对象，可以不打开。
- 原始输出有助于定位结构化解析失败原因。

### 生产中必须知道的问题

**问题：`include_raw=True` 有什么用？**

答：用于调试结构化输出，可以同时看到原始响应和解析结果。

## 综合练习

### 结构

定义一个 `CourseReview`，从学习反馈中抽取：

- 课程名
- 情绪分类
- 置信度
- 关键词列表
- 是否推荐

### 功能

练习 Pydantic 字段、`Literal`、数值范围和列表抽取。

### 使用步骤

1. 定义 `CourseReview`。
2. 使用 `with_structured_output(CourseReview)`。
3. 输入一段学习反馈。
4. 打印字段值。

### 注意项

- 分类字段用 `Literal`。
- 分数字段用 `ge`、`le`。
- 关键词字段用 `list[str]`。

### 生产中必须知道的问题

**问题：结构化输出失败时怎么排查？**

答：先打开 `include_raw=True` 查看原始输出，再检查 Schema 字段描述、类型约束和模型是否支持结构化输出。
