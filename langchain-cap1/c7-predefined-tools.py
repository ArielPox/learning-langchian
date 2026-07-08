import json
import os

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.structured_output import ToolStrategy
from langchain.tools import tool
from langchain_openai import ChatOpenAI
from langchain_tavily import TavilySearch
from pydantic import BaseModel, Field

# 预定义工具：LangChain 或第三方集成已经封装好的工具。
# 自定义工具：我们把预定义工具再包装一层，改造成更适合业务使用的工具。
# 结构化输出：让智能体最终返回 Pydantic 对象，而不是普通文本。


class SearchSource(BaseModel):
    """搜索来源。"""

    title: str = Field(description="来源标题")
    url: str = Field(description="来源链接")
    summary: str = Field(description="来源摘要")


class SearchReport(BaseModel):
    """智能体最终需要返回的结构化结果。"""

    question: str = Field(description="用户问题")
    answer: str = Field(description="综合回答")
    sources: list[SearchSource] = Field(description="参考来源列表")


# 第一步：加载 .env 文件中的环境变量。
load_dotenv()

# 第二步：创建模型对象。
model = ChatOpenAI(
    model="qwen3.6-plus",
    api_key=os.getenv("TONGYI_API_KEY"),
    base_url=os.getenv("ALIYUN_BASE_URL"),
    extra_body={"enable_thinking": False},
)

# 第三步：创建预定义 Tavily 工具。
# 使用真实 Tavily 搜索前，需要在 .env 中配置：
# TAVILY_API_KEY=你的 Tavily Key
tavily_api_key = os.getenv("TAVILY_API_KEY")
tavily_search = None

if tavily_api_key:
    tavily_search = TavilySearch(
        max_results=3,
        search_depth="basic",
        include_answer=True,
    )


# 第四步：把预定义 Tavily 工具包装成自定义工具。
# 这样可以统一返回格式，也可以在这里加入业务规则。
@tool
def search_web_with_tavily(query: str) -> str:
    """使用 Tavily 搜索网络信息，适合查询需要外部资料或最新信息的问题。"""
    if tavily_search is None:
        demo_result = {
            "query": query,
            "answer": "当前没有配置 TAVILY_API_KEY，这里返回教学用的模拟搜索结果。",
            "sources": [
                {
                    "title": "LangChain Structured Output",
                    "url": "https://docs.langchain.com/oss/python/langchain/structured-output",
                    "summary": "结构化输出可以让智能体按指定 schema 返回结果。",
                },
                {
                    "title": "LangChain Tools",
                    "url": "https://docs.langchain.com/oss/python/langchain/tools",
                    "summary": "工具可以把外部能力提供给模型或智能体调用。",
                },
            ],
        }
        return json.dumps(demo_result, ensure_ascii=False)

    raw_result = tavily_search.invoke({"query": query})
    sources = []

    for item in raw_result.get("results", []):
        sources.append(
            {
                "title": item.get("title", ""),
                "url": item.get("url", ""),
                "summary": item.get("content", ""),
            }
        )

    result = {
        "query": raw_result.get("query", query),
        "answer": raw_result.get("answer") or "",
        "sources": sources,
    }
    return json.dumps(result, ensure_ascii=False)


# 第五步：单独使用预定义 Tavily 工具。
print("========== 预定义 Tavily 工具 ==========")
if tavily_search is None:
    print("未配置 TAVILY_API_KEY，跳过真实 TavilySearch 调用。")
else:
    raw_search_result = tavily_search.invoke(
        {"query": "LangChain structured output 是什么？"}
    )
    print(json.dumps(raw_search_result, ensure_ascii=False, indent=2))

# 第六步：单独使用自定义 Tavily 工具。
print("\n========== 自定义 Tavily 工具 ==========")
custom_search_result = search_web_with_tavily.invoke(
    {"query": "LangChain structured output 是什么？"}
)
print(custom_search_result)

# 第七步：创建智能体。
# response_format 使用 ToolStrategy，表示最终答案也通过工具调用方式变成结构化对象。
agent = create_agent(
    model=model,
    tools=[search_web_with_tavily],
    response_format=ToolStrategy(SearchReport),
    system_prompt="""
你是一名研究助手。
回答问题前，必须先调用 search_web_with_tavily 工具。
最终回答必须整理成结构化结果：question、answer、sources。
""",
)

# 第八步：向智能体提问。
# 如果模型账号欠费、Key 错误或网络不可用，这里会调用失败。
try:
    response = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": "请搜索并总结：LangChain 的 structured output 是什么？",
                }
            ]
        }
    )
except Exception as error:
    print("\n========== 智能体调用失败 ==========")
    print("请检查 TONGYI_API_KEY、ALIYUN_BASE_URL、账号余额或网络连接。")
    print(error)
else:
    # 第九步：查看智能体完整消息。
    print("\n========== 智能体完整消息 ==========")
    for message in response["messages"]:
        message.pretty_print()

    # 第十步：读取结构化输出。
    structured_response = response["structured_response"]

    print("\n========== 结构化输出 ==========")
    print(structured_response.model_dump_json(indent=2))

    print("\n========== 读取结构化字段 ==========")
    # print(structured_response.answer)
    for source in structured_response.sources:
        print(f"- {source.title}: {source.url}")
