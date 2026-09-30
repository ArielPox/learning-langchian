# Cap4 Middleware 中间件章节笔记

## 1. Middleware 基础概念

### 结构

```python
agent = create_agent(
    model=model,
    tools=[...],
    middleware=[...],
)
```

### 功能

Middleware 是 Agent 执行流程中的拦截器，用来在模型调用、工具调用等关键节点插入额外逻辑。

常见用途：

- 记录模型调用和工具调用日志。
- 限制模型调用次数，控制成本。
- 在高风险工具执行前做审计或审批。
- 对模型调用或工具调用做重试、fallback、缓存。

### 使用步骤

1. 从 `langchain.agents.middleware` 导入中间件。
2. 创建内置中间件或自定义中间件。
3. 传入 `create_agent(..., middleware=[...])`。
4. 调用 Agent，并观察中间件日志。

### 注意项

- Middleware 管流程，不负责具体业务能力。
- Tool 管能力，Prompt 管行为倾向，Model 管推理和生成。
- 中间件顺序会影响执行效果。

### 生产中必须知道的问题

**问题：Middleware 和 Tool 的区别是什么？**

答：Tool 是 Agent 可调用的外部能力；Middleware 是 Agent 执行流程中的拦截和治理机制。

## 2. ModelCallLimitMiddleware

### 结构

```python
from langchain.agents.middleware import ModelCallLimitMiddleware

ModelCallLimitMiddleware(
    run_limit=4,
    exit_behavior="end",
)
```

### 功能

限制单次 Agent 运行中的模型调用次数，防止死循环和成本失控。

### 使用步骤

1. 导入 `ModelCallLimitMiddleware`。
2. 设置 `run_limit`。
3. 放入 Agent 的 `middleware` 列表。

```python
agent = create_agent(
    model=model,
    tools=tools,
    middleware=[
        ModelCallLimitMiddleware(run_limit=4, exit_behavior="end"),
    ],
)
```

### 注意项

- `run_limit` 太小会导致复杂任务未完成。
- 生产环境建议配置模型调用限制。
- `exit_behavior="end"` 表示达到限制后结束。

### 生产中必须知道的问题

**问题：为什么 Agent 需要模型调用次数限制？**

答：因为 Agent 可能在模型与工具之间多轮循环，限制调用次数可以控制成本和异常风险。

## 3. before_model

### 结构

```python
from langchain.agents.middleware import before_model

@before_model
def log_before_model(state, runtime) -> None:
    print(len(state["messages"]))
```

### 功能

在模型调用之前执行逻辑，适合打印日志、检查状态、做上下文治理。

### 使用步骤

1. 导入 `before_model`。
2. 写函数接收 `state` 和 `runtime`。
3. 使用装饰器生成中间件。
4. 注册到 Agent。

### 注意项

- 它发生在模型调用前，拿不到模型返回结果。
- 如果要包裹完整模型调用，应使用 `wrap_model_call`。

### 生产中必须知道的问题

**问题：`before_model` 适合做什么？**

答：适合在模型调用前观察和检查 Agent 状态，例如消息数量、上下文长度、是否需要提前终止。

## 4. wrap_model_call

### 结构

```python
from langchain.agents.middleware import wrap_model_call

@wrap_model_call
def log_model_call(request, handler):
    print("模型调用前")
    response = handler(request)
    print("模型调用后")
    return response
```

### 功能

包裹一次完整模型调用，可在调用前后加入日志、重试、fallback 或请求改写。

适合做：

- 模型调用日志。
- 模型调用耗时统计。
- 模型失败重试。
- 主模型失败后切换备用模型。
- 修改模型请求或响应。

### 使用步骤

1. 导入 `wrap_model_call`。
2. 定义接收 `request` 和 `handler` 的函数。
3. 在函数中调用 `handler(request)`。
4. 返回模型响应。
5. 把中间件放入 `middleware` 列表。

### 注意项

- 必须调用 `handler(request)`，否则模型不会执行。
- 必须返回响应，否则 Agent 后续流程无法继续。
- 不要把具体业务能力写在这里，业务能力应放在 Tool 中。

### 生产中必须知道的问题

**问题：`handler(request)` 是什么？**

答：它代表真正的模型调用。中间件通过包裹它，在模型调用前后插入逻辑。

## 5. Node 型 Hook：before_agent / after_agent / before_model / after_model

### 结构

除了 `wrap_*` 这种包裹型中间件，还有一类更像“节点”的 hook：

```python
from langchain.agents.middleware import (
    before_agent,
    after_agent,
    before_model,
    after_model,
)
```

常见写法：

```python
@before_model
def log_before_model(state, runtime) -> None:
    print("模型调用前")
    print(len(state["messages"]))


@after_model
def log_after_model(state, runtime) -> None:
    print("模型调用后")
```

它们不像 `wrap_model_call` 那样通过 `handler(request)` 包住一次调用，而是在 Agent 执行图的某个位置插入一个 hook。

可以粗略理解为：

```text
before_agent：Agent 整体运行开始前
before_model：每次模型节点运行前
after_model：每次模型节点运行后
after_agent：Agent 整体运行结束后
```

### 功能

Node 型 hook 更适合做“某个阶段前后”的状态检查或状态更新。

适合做：

- Agent 开始前记录输入。
- Agent 结束后记录最终状态。
- 模型调用前检查消息数量。
- 模型调用后检查模型是否产出了工具调用。
- 根据状态更新 Agent state。
- 必要时控制流程跳转，例如提前结束。

`wrap_*` 更适合包裹一次真实调用。

对比：

```text
before_model / after_model：在模型节点前后插入逻辑。
wrap_model_call：包住真正的模型调用，可以处理调用前、调用后和异常。

before_agent / after_agent：在 Agent 整体运行前后插入逻辑。
wrap_tool_call：包住真正的工具调用。
```

### 使用步骤

1. 选择 hook 位置。

```text
想在 Agent 开始前执行：before_agent
想在 Agent 结束后执行：after_agent
想在每次模型调用前执行：before_model
想在每次模型调用后执行：after_model
想包住模型调用并处理异常：wrap_model_call
想包住工具调用并审计参数：wrap_tool_call
```

2. 编写 hook 函数。

```python
@before_agent
def log_agent_start(state, runtime) -> None:
    print("Agent 开始运行")


@after_agent
def log_agent_end(state, runtime) -> None:
    print("Agent 运行结束")
```

3. 注册到 Agent。

```python
agent = create_agent(
    model=model,
    tools=tools,
    middleware=[
        log_agent_start,
        log_before_model,
        log_after_model,
        log_agent_end,
    ],
)
```

4. 运行时观察触发次数。

如果一次任务调用了两次模型，那么：

```text
before_agent：执行 1 次
before_model：执行 2 次
after_model：执行 2 次
after_agent：执行 1 次
```

### 注意项

- `before_model` 和 `after_model` 可能执行多次，因为一次 Agent 任务可能多次调用模型。
- `before_agent` 和 `after_agent` 通常围绕一次完整 Agent 运行。
- Node 型 hook 不需要 `handler(request)`。
- 如果你需要捕获模型调用异常、做重试或 fallback，优先用 `wrap_model_call`。
- 如果你只想看模型调用前后的 state，用 `before_model` / `after_model` 更简单。
- 如果 hook 修改 state，要确保返回的数据结构符合 Agent state 要求。

### 生产中必须知道的问题

**问题：Node 型 hook 和 wrap 型 hook 最大区别是什么？**

答：Node 型 hook 是在执行图某个阶段前后插入逻辑；wrap 型 hook 是包住一次真实调用，需要通过 `handler(request)` 放行。

**问题：为什么 `before_model` 也可以看作 node？**

答：因为 Agent 底层基于 LangGraph，模型调用本身是图里的一个节点。`before_model` 就是在模型节点前插入逻辑，所以它更像执行图中的一个阶段性 hook。

**问题：什么时候用 Node 型 hook，什么时候用 wrap？**

答：只检查状态或记录日志，用 Node 型 hook；需要包住真实调用、处理异常、重试、fallback、缓存、改写请求或响应，用 wrap。

**问题：`before_agent` 和 `before_model` 有什么区别？**

答：`before_agent` 在一次 Agent 运行开始前执行，通常一次任务执行一次；`before_model` 在每次模型调用前执行，一次任务中可能执行多次。

**问题：`after_agent` 适合做什么？**

答：适合做最终日志记录、结果审计、指标上报、清理临时状态等收尾工作。

## 6. wrap_tool_call

### 结构

```python
from langchain.agents.middleware import wrap_tool_call

@wrap_tool_call
def audit_tool_call(request, handler):
    tool_name = request.tool_call["name"]
    tool_args = request.tool_call["args"]
    result = handler(request)
    return result
```

### 功能

包裹一次工具调用，适合做工具审计、参数校验、缓存、重试或高风险审批。

适合做：

- 打印工具名称和参数。
- 记录工具调用日志。
- 高风险工具执行前审批。
- 工具失败后重试。
- 工具结果缓存。
- 工具参数校验。

### 使用步骤

1. 导入 `wrap_tool_call`。
2. 读取 `request.tool_call["name"]` 和 `request.tool_call["args"]`。
3. 工具执行前做审计。
4. 调用 `handler(request)` 真正执行工具。
5. 返回工具结果。

### 注意项

- 发邮件、删文件、转账等外部副作用操作应重点审计。
- 可以在这里接入人工审批。
- 不要随意修改工具参数，除非明确知道业务后果。

### 生产中必须知道的问题

**问题：如何拦截高风险工具调用？**

答：使用 `wrap_tool_call` 判断工具名和参数，在执行 `handler(request)` 前加入审批或拒绝逻辑。

## 7. wrap_model_call 与 wrap_tool_call 的执行顺序

### 结构

准确名称是：

- `wrap_model_call`
- `wrap_tool_call`

注意是 `wrap`，不是 `warp`。`wrap` 的意思是“包裹”，表示在真正的模型调用或工具调用外面包一层逻辑。

一次典型 Agent 请求，如果需要调用工具，整体流程如下：

```text
用户输入
  -> before_model
  -> wrap_model_call 开始
  -> handler(request) 真正调用模型
  -> 模型决定是否调用工具
  -> wrap_model_call 结束
  -> 如果模型要求调用工具
  -> wrap_tool_call 开始
  -> handler(request) 真正执行工具
  -> wrap_tool_call 结束
  -> 工具结果加入 messages
  -> before_model 再次执行
  -> wrap_model_call 再次执行
  -> 模型根据工具结果生成最终回答
  -> 返回最终结果
```

所以它们不是简单地各执行一次，而是经常形成这个节奏：

```text
wrap_model_call -> wrap_tool_call -> wrap_model_call
```

如果任务需要多个工具，可能是：

```text
wrap_model_call
  -> wrap_tool_call
  -> wrap_model_call
  -> wrap_tool_call
  -> wrap_model_call
```

### 功能

`wrap_model_call` 负责拦截模型调用。

`wrap_tool_call` 负责拦截工具调用。

在 Agent 中，模型和工具的关系通常是：

```text
模型负责决定要不要调用工具
工具负责执行具体外部能力
模型再根据工具结果组织最终回答
```

因此一次看似简单的用户请求，也可能触发多次模型调用。

### 使用步骤

1. 编写 `wrap_model_call`。

```python
@wrap_model_call
def log_model_call(request, handler):
    print("模型调用开始")
    response = handler(request)
    print("模型调用结束")
    return response
```

2. 编写 `wrap_tool_call`。

```python
@wrap_tool_call
def audit_tool_call(request, handler):
    tool_name = request.tool_call["name"]
    tool_args = request.tool_call["args"]

    print(f"工具名称：{tool_name}")
    print(f"工具参数：{tool_args}")

    result = handler(request)
    return result
```

3. 注册到 Agent。

```python
agent = create_agent(
    model=model,
    tools=[get_weather, send_email],
    middleware=[
        log_model_call,
        audit_tool_call,
    ],
)
```

4. 观察执行顺序。

如果用户请求是：

```text
请查询北京天气，然后给 amy@example.com 发邮件。
```

可能出现的执行过程是：

```text
第 1 次 wrap_model_call
  模型分析任务，决定调用 get_weather

第 1 次 wrap_tool_call
  执行 get_weather

第 2 次 wrap_model_call
  模型看到天气结果，决定调用 send_email

第 2 次 wrap_tool_call
  执行 send_email

第 3 次 wrap_model_call
  模型根据工具结果生成最终回答
```

有些模型也可能一次性发出多个工具调用，所以具体次数取决于模型、工具和任务复杂度。

### 注意项

- `handler(request)` 必须调用。

在 `wrap_model_call` 中：

```python
response = handler(request)
```

这才是真正调用模型。

在 `wrap_tool_call` 中：

```python
result = handler(request)
```

这才是真正执行工具。

- 必须返回结果。

```python
return response
return result
```

如果不返回，Agent 后续流程拿不到模型响应或工具结果。

- 不调用 `handler(request)` 就等于拦截不放行。

这种写法可以用于缓存、拒绝危险操作、提前返回兜底结果，但要明确知道自己在终止后续流程。

- 工具调用前后要特别小心副作用。

以下工具属于高风险工具：

```text
send_email
delete_file
transfer_money
update_database
run_shell_command
```

这些工具一旦执行，就可能改变真实世界。生产中应该在 `wrap_tool_call` 中做审计、权限校验或人工确认。

- `ModelCallLimitMiddleware` 会影响整个链路。

例如：

```python
ModelCallLimitMiddleware(run_limit=4)
```

如果任务需要：

```text
模型 -> 工具 -> 模型 -> 工具 -> 模型
```

那模型可能需要调用 3 次。`run_limit` 太小，任务可能还没完成就被截断。

### 生产中必须知道的问题

**问题：`wrap_model_call` 和 `wrap_tool_call` 谁先执行？**

答：通常是 `wrap_model_call` 先执行，因为 Agent 要先调用模型判断是否需要工具；如果模型决定调用工具，才会进入 `wrap_tool_call`；工具返回后，通常还会再次进入 `wrap_model_call` 生成最终回答。

**问题：为什么 `wrap_model_call` 可能执行多次？**

答：因为 Agent 需要先调用模型做决策，工具执行完成后，还需要再次调用模型根据工具结果组织最终回答。复杂任务中，模型和工具可能交替执行多轮。

**问题：`handler(request)` 在两个 wrap 中分别代表什么？**

答：在 `wrap_model_call` 中，`handler(request)` 代表真正调用模型；在 `wrap_tool_call` 中，`handler(request)` 代表真正执行工具。

**问题：如果忘记调用 `handler(request)` 会怎样？**

答：模型或工具不会真正执行，Agent 流程会被中断。除非你明确想拦截、缓存或拒绝操作，否则一般都要调用。

**问题：生产中哪些逻辑适合放在 `wrap_tool_call`？**

答：工具审计、权限校验、参数检查、危险操作审批、工具结果缓存、工具重试等。尤其是发邮件、删数据、转账、执行命令这类有副作用的工具。

## 综合练习

### 结构

构建一个办公助手：

- 查询天气工具
- 查询会议室工具
- 发送邮件工具
- 模型调用限制
- 工具调用审计

### 功能

练习 Middleware 对 Agent 执行流程的治理能力。

### 使用步骤

1. 定义三个工具。
2. 使用 `ModelCallLimitMiddleware(run_limit=6)`。
3. 使用 `before_model` 打印消息数量。
4. 使用 `wrap_tool_call` 审计工具调用。
5. 观察日志顺序。

### 注意项

- 一次用户请求可能触发多次模型调用。
- 工具执行后通常还会再次调用模型总结结果。
- 复杂任务要给足 `run_limit`。

### 生产中必须知道的问题

**问题：Middleware 的核心价值是什么？**

答：把日志、限流、审计、审批、重试等工程化能力从核心业务逻辑中拆出来，让 Agent 更可控、更可维护。

## 8. Middleware 高频生产问题补充

### 结构

这一节专门整理中间件相关的高频追问。

重点围绕：

- 中间件和 Tool、Prompt、Memory 的边界。
- 多个中间件的执行顺序。
- 中间件适合放哪些逻辑。
- 生产环境如何做安全、限流、日志、重试。
- 如何排查 Agent 没有按预期调用工具。

### 功能

帮助你从“会写中间件”提升到“知道中间件在生产中怎么设计”。

中间件不是为了炫技，而是为了解决工程化问题：

```text
可观测性：日志、链路追踪、耗时统计
稳定性：重试、fallback、异常兜底
安全性：审批、权限、敏感信息处理
成本控制：模型调用限制、工具调用限制、上下文压缩
治理能力：统一规则、统一审计、统一拦截
```

### 使用步骤

设计生产级 Middleware 时，可以按这个顺序思考：

1. 先判断这个逻辑是业务能力，还是流程治理。
2. 如果是业务能力，优先放到 Tool。
3. 如果是模型行为倾向，优先放到 Prompt。
4. 如果是会话历史，优先放到 Memory 或 checkpointer。
5. 如果是拦截、审计、限流、重试、审批，再放到 Middleware。
6. 每个中间件只做一类事情，避免变成“大杂烩”。
7. 上线前用日志验证执行顺序和触发条件。

### 注意项

- 不要把业务主流程全部塞进 Middleware。
- 不要在 Middleware 里悄悄修改用户输入，除非有清晰日志。
- 不要在 `wrap_tool_call` 中无记录地放行高风险操作。
- 不要只依赖 Prompt 阻止危险工具调用，Prompt 是软约束，中间件才适合做硬拦截。
- 不要忘记 `return handler(request)` 或返回自定义结果。
- 生产中建议至少具备日志、限流、错误处理和高风险工具审计。

### 生产中必须知道的问题

**问题：Middleware、Tool、Prompt、Memory 分别适合放什么？**

答：

```text
Tool：具体业务能力，例如查天气、查数据库、发邮件。
Prompt：模型角色、回答风格、任务规则。
Memory：会话历史、长期偏好、跨轮上下文。
Middleware：流程治理，例如日志、限流、审计、审批、重试、fallback。
```

**问题：什么时候一定要用 Middleware，而不是只写 Prompt？**

答：当你需要硬控制时应该用 Middleware。例如限制调用次数、拦截高风险工具、记录审计日志、失败后重试、切换备用模型。这些都不应该只靠 Prompt。

**问题：多个 Middleware 同时存在时，如何设计顺序？**

答：一般建议先放全局限制类，再放日志类，再放业务审计类，最后放特殊处理类。实际顺序要通过日志验证，因为不同 hook 作用在不同阶段。

**问题：为什么 Agent 没有调用我定义的工具？**

答：常见原因有：

- 工具名不清晰。
- docstring 描述不明确。
- 参数类型不清楚。
- 用户问题没有明显触发工具的需求。
- `system_prompt` 没有明确要求使用工具。
- 模型认为自己可以直接回答。

解决方式是优化工具名、参数描述、docstring，并在 `system_prompt` 中明确“遇到某类问题必须调用某工具”。

**问题：为什么工具已经执行了，最终回答里却没体现工具结果？**

答：工具执行后，通常还要再次调用模型组织最终回答。如果模型没有正确利用工具结果，可能是工具返回内容不清楚、系统提示词不明确，或者模型调用次数被 `ModelCallLimitMiddleware` 截断了。

**问题：`before_model`、`wrap_model_call`、`after_model` 怎么选？**

答：

```text
before_model：只关心模型调用前的状态。
wrap_model_call：需要包裹完整模型调用，能处理调用前、调用后和异常。
after_model：只关心模型调用后的状态。
```

如果要做重试、fallback、耗时统计，通常选 `wrap_model_call`。

**问题：`wrap_tool_call` 和 Human-in-the-loop 有什么关系？**

答：`wrap_tool_call` 可以自己实现工具调用前审批；`HumanInTheLoopMiddleware` 是 LangChain 提供的更标准的人工介入中间件。简单审计可以自定义，复杂审批流程建议使用内置方案或接入业务审批系统。

**问题：如何给工具调用做缓存？**

答：可以在 `wrap_tool_call` 中根据工具名和参数生成缓存 key。如果缓存存在，直接返回缓存结果；如果不存在，再执行 `handler(request)` 并保存结果。

**问题：如何做模型 fallback？**

答：可以在 `wrap_model_call` 中先调用主模型，如果异常，再切换到备用模型后重新调用。生产中也可以使用内置的 `ModelFallbackMiddleware`。

**问题：如何做模型重试和工具重试？**

答：模型调用失败适合用 `wrap_model_call` 或内置 `ModelRetryMiddleware`；工具调用失败适合用 `wrap_tool_call` 或内置 `ToolRetryMiddleware`。

**问题：Middleware 会不会影响结构化输出？**

答：会。因为结构化输出本质上也需要经过模型调用，有些策略还会生成伪工具消息。如果中间件修改了模型请求、响应或消息历史，可能影响结构化输出结果。

**问题：Middleware 能不能修改用户消息？**

答：技术上可以，但生产中要谨慎。修改用户消息会影响审计和可解释性，必须记录原始输入和修改后的输入，并明确修改原因。

**问题：Middleware 中如何处理异常？**

答：可以捕获异常后重试、fallback、返回兜底结果或继续抛出。原则是：可恢复错误做重试，不可恢复错误要清晰失败，不要吞掉异常导致问题难以排查。

**问题：中间件会不会增加延迟？**

答：会。日志、审批、重试、额外模型调用都会增加延迟。生产中要权衡安全性、稳定性和响应速度。

**问题：如何判断一个中间件设计得好不好？**

答：好的中间件应该职责单一、可复用、可观测、可配置、失败行为清晰，并且不隐藏关键业务逻辑。

**问题：生产环境最少应该配置哪些 Middleware？**

答：至少建议配置：

- 模型调用限制。
- 工具调用审计。
- 高风险工具审批。
- 模型或工具失败重试。
- 日志与耗时统计。

具体是否使用内置中间件或自定义中间件，要看业务复杂度。
