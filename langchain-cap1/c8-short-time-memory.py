from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver
import os 
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv


#load .env variable
load_dotenv()

#create model obj
model=ChatOpenAI(
    model="qwen3.7-plus",
    api_key=os.getenv("TONGYI_API_KEY"),
    base_url=os.getenv("ALIYUN_BASE_URL"),
)

#create short-time memory storage
memory=InMemorySaver()

# agent with short-time memory created
agent=create_agent(
    model=model,
    tools=[],
    checkpointer=memory,
    system_prompt="""
    you are a patient teacher,teacher me how to use langchain
    """
)


def ask(ques:str,thread_id:str)->None:
    """"向同一个智能提问 使用的thread——id不同的对话"""
    config={
        "configurable":{
            "thread_id":thread_id,
        }
    }

    response=agent.invoke(
        {
            "messages":[
                {
                    "role":"user",
                    "content":ques
                }
            ]
        },
        config=config
    )
    print(f"------------session{thread_id}--------")
    print(f"--------用户：{ques}---------------")
    print(f"助手：{response['messages'][-1].content}")

#constant ques in the same session
try:
    ask('my name is sinda, Iam studing langchain now',thread_id='study-sinda')
    ask("what are my name I mentioned,what skill i learning,",thread_id="study-sinda")
except Exception as error:
    print("fail to use agent")
    print(error)

# 学习重点：
# 1. checkpointer 负责保存短期记忆。
# 2. thread_id 负责区分不同会话。
# 3. 同一个 thread_id 会继承历史消息，不同 thread_id 互不影响。
# 4. InMemorySaver 只保存在内存中，程序结束后记忆会消失。