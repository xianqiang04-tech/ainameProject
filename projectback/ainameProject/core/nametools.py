import asyncio
from langchain_deepseek import ChatDeepSeek
from langchain_core.prompts import ChatPromptTemplate
from openai import max_retries
# from sentry_sdk.integrations import aiohttp

from schemas.name_schemas import NameResultSchema, NameIn
from dotenv import load_dotenv
import os
# 读取项目根目录下的 .env 文件
load_dotenv()

llm = ChatDeepSeek(
    model="deepseek-v4-pro",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    temperature=0.5,
    timeout=120,
    extra_body={
        "thinking":{
            "type":"disabled"
        }
    }
)

system_prompt = """你是一位精通汉语言文学与传统文化的命名专家。请为用户创作富有文化底蕴的人
名。
原则：平仄协调，寓意深远，优先从《诗经》《楚辞》或唐诗宋词中汲取灵感。
请给出 5 个候选方案。"""

prompt_template = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("user","【姓氏】:{surname} 【性别】:{gender} 【字数限制】:{length} 【其它要求】:{other} 【避讳字】:{exclude}")
])

structured_llm = llm.with_structured_output(NameResultSchema)
chain = prompt_template | structured_llm

async def generate_name(name_info:NameIn):
    max_retries = 3
    for attempt in range(max_retries):
        try:
            result = await chain.ainvoke({
                "surname": name_info.surname,
                "gender": name_info.gender,
                "length": name_info.length,
                "other": name_info.other,
                "exclude": name_info.exclude
            })
            if result is not None:
                return result
        except Exception as e:
            print(f"❌ 第 {attempt + 1} 次请求遭遇网络异常: {e}，正在重试...")

# async def main():
#     name_info = NameIn(
#         surname="张",
#         gender="女",
#         length="两字",
#         other="希望名字里带点水的意象",
#         exclude=["李", "王"]
#     )
#
#     names = await generate_name(name_info)
#     print("最终结果:", names)
#
# if __name__ == '__main__':
#     asyncio.run(main())