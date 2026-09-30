import os
from pprint import pprint

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.middleware import (
    ModelCallLimitMiddleware,
    before_model,
    wrap_model_call,
    wrap_tool_call,
)
from langchain.chat_models import init_chat_model
from langchain.tools import tool


"""
LangChain Agent Middleware 教学示例

中间件可以理解为 Agent 执行过程中的“拦截器”。
它不直接负责回答问题，而是在模型调用、工具调用等关键节点上插入额外逻辑。

常见用途：
1. 记录日志：看 Agent 到底调用了几次模型、几次工具。
2. 成本控制：限制模型调用次数、工具调用次数。
3. 安全控制：调用危险工具前先审批，或屏蔽敏感信息。
4. 容错增强：模型失败后重试，或切换备用模型。
"""


load_dotenv()

model = init_chat_model(
    model="qwen-plus",
    model_provider="openai",
    api_key=os.getenv("TONGYI_API_KEY"),
    base_url=os.getenv("ALIYUN_BASE_URL"),
)


@tool(parse_docstring=True)
def get_weather(city: str) -> str:
    """查询指定城市的天气。

    Args:
        city: 城市名称，例如北京、上海、广州。
    """
    return f"{city}今天晴，气温 22 到 28 摄氏度。"


@tool(parse_docstring=True)
def send_email(recipient: str, subject: str, body: str) -> str:
    """模拟发送邮件。

    Args:
        recipient: 收件人邮箱。
        subject: 邮件标题。
        body: 邮件正文。
    """
    return f"已模拟发送邮件给 {recipient}，标题：{subject}，正文：{body}"


@before_model
def log_before_model(state, runtime) -> None:
    """模型调用前触发。

    适合做：打印日志、检查消息数量、提前拦截不合规请求等。
    """
    print("\n[before_model] 即将调用模型")
    print(f"[before_model] 当前消息数量：{len(state['messages'])}")


@wrap_model_call
def log_model_call(request, handler):
    """包裹一次模型调用。

    handler(request) 才是真正调用模型的动作。
    所以：
    - handler 之前：模型调用前逻辑
    - handler 之后：模型调用后逻辑
    """
    print("\n[wrap_model_call] 模型调用开始")
    print(f"[wrap_model_call] 本次发送给模型的消息数：{len(request.messages)}")

    response = handler(request)

    print("[wrap_model_call] 模型调用结束")
    print(f"[wrap_model_call] 模型返回消息数：{len(response.result)}")
    return response


@wrap_tool_call
def audit_tool_call(request, handler):
    """包裹一次工具调用。

    这里演示“工具调用审计”：在工具真正执行前打印工具名和参数。
    如果是发邮件、转账、删文件这类高风险工具，也可以在这里加入人工审批。
    """
    tool_name = request.tool_call["name"]
    tool_args = request.tool_call["args"]

    print("\n[wrap_tool_call] 准备调用工具")
    print(f"[wrap_tool_call] 工具名称：{tool_name}")
    print(f"[wrap_tool_call] 工具参数：{tool_args}")

    if tool_name == "send_email":
        print("[wrap_tool_call] 这里可以接入人工审批；本示例直接放行。")

    result = handler(request)

    print("[wrap_tool_call] 工具调用完成")
    return result


agent = create_agent(
    model=model,
    tools=[get_weather, send_email],
    system_prompt=(
        "你是一个中文助理。"
        "用户询问天气时必须调用 get_weather 工具。"
        "用户要求发邮件时必须调用 send_email 工具。"
    ),
    middleware=[
        # 内置中间件：限制一次 agent.invoke 里最多调用 4 次模型，避免 Agent 死循环。
        ModelCallLimitMiddleware(run_limit=4, exit_behavior="end"),
        # 自定义中间件：模型调用前日志。
        log_before_model,
        # 自定义中间件：包裹模型调用，记录调用前后。
        log_model_call,
        # 自定义中间件：包裹工具调用，记录工具名和参数。
        audit_tool_call,
    ],
)


def print_final_answer(result: dict) -> None:
    """从 Agent 返回的消息列表里取最后一条 AI 回复。"""
    print("\n========== Agent 最终返回 ==========")
    pprint(result["messages"][-1])


if __name__ == "__main__":
    response = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": (
                        "请查询北京今天的天气，"
                        "然后给 amy@example.com 发一封邮件，"
                        "标题是“天气提醒”，正文总结一下天气。"
                    ),
                }
            ]
        }
    )

    print_final_answer(response)
