import base64
import mimetypes
import os
from pathlib import Path
from dotenv import load_dotenv
from IPython.display import Image, display
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI

# 多模态消息：一条消息中可以同时包含文字、图片等不同类型的内容。
def local_image_to_data_url(image_path: str) -> str:
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode()


# 第一步：加载 .env 文件中的环境变量。
load_dotenv()

# 第二步：创建支持图片理解的视觉模型。
model = init_chat_model(
    model="qwen3.7-plus",
    model_provider="openai",
    api_key=os.getenv("TONGYI_API_KEY"),
    base_url=os.getenv("ALIYUN_BASE_URL"),
)

# 第三步：准备图片。
image_url = "test.png"

# 第四步：创建一条多模态消息。
# content 是一个列表，其中包含文字和图片两个内容块。
message = HumanMessage(
    # content=[
    #     {
    #         "type": "text",
    #         "text": "请用一句话描述这张图片。",
    #     },
    #     {
    #         "type": "image_url",
    #         "image_url": {
    #             "url": image_url,
    #         },
    #     },
    # ]
    #推荐写法 是懒加载的content_block 懒加载就是消息对象创建时不读取图片等大资源，仅在调用模型发送请求时才加载处理，减少内存占用、便于消息序列化存储
    content_blocks=[
        {
            'type':'text','text':'一句话描述图片'
        },
        {
            'type':'image',
            'base64': local_image_to_data_url(image_url),
            'mime_type': 'image/png'
        }
    ]

)


# 第五步：将多模态消息发送给模型。
response = model.invoke([message])

# 第六步：输出模型对图片的理解结果。
print(response.content_blocks)
