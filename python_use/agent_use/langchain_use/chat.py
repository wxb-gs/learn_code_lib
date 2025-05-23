import asyncio
from time import sleep
# 改为从新包导入
from langchain_ollama import ChatOllama  # ✅ 正确导入方式
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import  ChatOpenAI
# 初始化模型
model = ChatOpenAI(model="qwen2:7b", base_url="127.0.0.1:10087")  # 使用新包中的类

async def run():
    # 方法1: 异步流式调用
    print("\n--- 方法1 ---")
    async for chunk in model.astream("天空的颜色是什么？"):
        print(chunk.content, end="", flush=True)
    
    print("next???????")
    
    # 方法2: 使用LCEL链式处理
    print("\n\n--- 方法2 ---")
    prompt = ChatPromptTemplate.from_template("讲一个关于{topic}的笑话")
    chain = prompt | model | StrOutputParser()
    
    async for chunk in chain.astream({"topic": "鹦鹉"}):
        print(chunk, end="", flush=True)
    sleep(2)
    print("\n你好")

if __name__ == '__main__':
    asyncio.run(run()) # 等待run方法执行完后，才会执行后续的内容
    print("what are you doing?")