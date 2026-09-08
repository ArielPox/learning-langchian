import os

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model

# 加载 .env 文件中的环境变量
load_dotenv()

# create model obj
model = init_chat_model(
    model="qwen-plus",
    model_provider="openai",
    api_key=os.getenv("TONGYI_API_KEY"),
    base_url=os.getenv("ALIYUN_BASE_URL"),
)


# 工具定义
def weather_query(city: str):
    """查询城市天气"""
    return f"{city}天气结果"


def math_calculate(expression: str):
    """复杂数学运算"""
    return eval(expression)


def time_query(offset_days: int = -1):
    """获取当前时间、日期计算"""
    from datetime import datetime, timedelta

    now = datetime.now()
    if offset_days is not None:
        now += timedelta(days=offset_days)
    return now.strftime("%Y-%m-%d %H:%M:%S")


def currency_convert(from_currency: str, to_currency: str, amount: float):
    """货币转换"""
    return {"result": amount, "from": from_currency, "to": to_currency}


def info_search(query: str):
    """信息搜索"""
    return f"搜索【{query}】返回的新闻/产品信息"


# 创建的多功能助手
class MultiFuncAssistant:
    def __init__(self) -> None:
        self.model = model

        self.tools = [
            weather_query,
            math_calculate,
            time_query,
            currency_convert,
            info_search,
        ]

        # 提示词
        system_prompt = """ 你是一个多功能助手，可以帮助用户
            天气查询：使用get_weather工具
            数学计算：math_calculate,
            使用时间查询：time_query,
            货币转换：currency_convert
            信息搜索：info_search

            始终使用中文回答
        """

        # 创建agent
        self.agent = create_agent(
            model=self.model, tools=self.tools, system_prompt=system_prompt
        )

        # 对话历史
        self.message = []

    def chat(self, user_input: str) -> str:
        """对话接口"""
        # 添加用户信息
        self.message.append({"role": "user", "content": user_input})

        # 调用agent
        result = self.agent.invoke({"messages": self.message})

        # 更新历史消息
        self.message = result["messages"]

        # 返回最后一条消息
        for msg in reversed(self.message):
            if msg.type == "ai" and msg.content:
                return msg.content
        return "can`t cope with this request"

    def reset(self):
        """重置会话历史"""
        self.message = []


# ==================== 主程序 ====================


def main():
    assistant = MultiFuncAssistant()

    print("=" * 40)
    print("🤖 多功能智能助手（LangChain 1.2）")
    print("=" * 40)
    print("\n我可以帮你：")
    print("  🌤  查询天气")
    print("  🔢 数学计算")
    print("  ⏰ 时间查询")
    print("  💱 货币转换")
    print("  🔍 信息搜索")
    print("\n输入 'quit' 退出，输入 'reset' 重置对话\n")

    demos = [
        "北京今天天气怎么样？",
        "帮我算一下 (25 + 17) * 3",
        "现在几点了？",
        "100 美元等于多少人民币？",
    ]

    for demo in demos:
        print(f"👤 {demo}")
        response = assistant.chat(demo)
        print(f"🤖 {response}\n")

    # 重置对话
    assistant.reset()

    # 交互模式
    print("=" * 40)
    print("💬 进入交互模式")
    print("=" * 40)

    while True:
        user_input = input("\n👤 你: ")

        if user_input.lower() == "quit":
            print("再见！👋")
            break

        if user_input.lower() == "reset":
            assistant.reset()
            print("✅ 对话已重置")
            continue

        if not user_input.strip():
            continue

        # 调用助手
        response = assistant.chat(user_input)
        print(f"🤖 助手: {response}")


if __name__ == "__main__":
    main()
