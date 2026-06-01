import base64
import mimetypes
import os
from pathlib import Path

from dotenv import load_dotenv
from IPython.display import Image, display
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI

# 多模态消息：一条消息中可以同时包含文字、图片等不同类型的内容。


def local_image_to_data_url(image_path: str) -> str:
    """将本地图片转换成模型可以接收的 Base64 Data URL。"""
    path = Path(image_path)
    mime_type, _ = mimetypes.guess_type(path.name)

    if mime_type is None or not mime_type.startswith("image/"):
        raise ValueError("无法识别图片格式，请使用 png、jpg 或 webp 图片。")

    image_base64 = base64.b64encode(path.read_bytes()).decode("utf-8")
    return f"data:{mime_type};base64,{image_base64}"


# 第一步：加载 .env 文件中的环境变量。
load_dotenv()

# 第二步：创建支持图片理解的视觉模型。
model = ChatOpenAI(
    model="qwen3-vl-plus",
    api_key=os.getenv("TONGYI_API_KEY"),
    base_url=os.getenv("ALIYUN-BASE-URL"),
)

# 第三步：准备图片。
# 方法一：使用公网图片 URL。
image_url = "https://dashscope.oss-cn-beijing.aliyuncs.com/images/dog_and_girl.jpeg"

# 方法二：使用本地图片。
# 在 .env 中设置 LOCAL_IMAGE_PATH 后，将优先加载本地图片，例如：
# LOCAL_IMAGE_PATH=D:\images\example.jpg
local_image_path = os.getenv("LOCAL_IMAGE_PATH")

if local_image_path:
    # 在 Jupyter Notebook 中预览本地图片。
    display(Image(filename=local_image_path))
    image_url = local_image_to_data_url(local_image_path)

# 第四步：创建一条多模态消息。
# content 是一个列表，其中包含文字和图片两个内容块。
message = HumanMessage(
    content=[
        {
            "type": "text",
            "text": "请用一句话描述这张图片。",
        },
        {
            "type": "image_url",
            "image_url": {
                "url": image_url,
            },
        },
    ]
)

# 第五步：将多模态消息发送给模型。
response = model.invoke([message])

# 第六步：输出模型对图片的理解结果。
response.pretty_print()
