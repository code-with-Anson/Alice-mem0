import json
import os
from typing import List

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel
from tenacity import retry, stop_after_attempt, wait_exponential

from app.utils.prompts import MEMORY_CATEGORIZATION_PROMPT

load_dotenv()

openai_client = OpenAI(
    base_url=os.environ.get("OPENAI_BASE_URL"), api_key=os.environ.get("OPENAI_API_KEY")
)


class MemoryCategories(BaseModel):
    categories: List[str]


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=15))
def get_categories_for_memory(memory: str) -> List[str]:
    """Get categories for a memory."""
    try:
        # 替换 responses.parse 方法，使用 chat.completions.create 代替
        response = openai_client.chat.completions.create(
            model=os.environ.get("OPENAI_MODEL", "deepseek-chat"),
            messages=[
                {"role": "system", "content": MEMORY_CATEGORIZATION_PROMPT},
                {"role": "user", "content": memory},
            ],
            temperature=0,
            response_format={"type": "json_object"},  # 请求 JSON 格式的响应
        )

        # 从响应中提取 JSON
        response_text = response.choices[0].message.content
        response_json = json.loads(response_text)

        # 提取并处理类别
        categories = response_json.get("categories", [])
        categories = [cat.strip().lower() for cat in categories]

        return categories
    except Exception as e:
        print(f"Error categorizing memory: {e}")
        return []  # 返回空列表而不是抛出异常，这样即使分类失败也不会中断程序


# @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=15))
# def get_categories_for_memory(memory: str) -> List[str]:
#     """Get categories for a memory."""
#     try:
#         response = openai_client.responses.parse(
#             model=os.environ.get("OPENAI_MODEL"),
#             instructions=MEMORY_CATEGORIZATION_PROMPT,
#             input=memory,
#             temperature=0,
#             text_format=MemoryCategories,
#         )
#         response_json = json.loads(response.output[0].content[0].text)
#         categories = response_json["categories"]
#         categories = [cat.strip().lower() for cat in categories]
#         # TODO: Validate categories later may be
#         return categories
#     except Exception as e:
#         raise e
