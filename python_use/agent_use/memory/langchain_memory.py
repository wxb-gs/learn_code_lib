import os
import uuid

from IPython.display import Image, display
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, MessagesState, StateGraph
from langchain_openai import ChatOpenAI


# Define a new graph
workflow = StateGraph(state_schema=MessagesState)

# Define a chat model
### 设置环境
os.environ["OPENAI_API_KEY"] =  'sk-d58877221cec4f208dc353259ca9c8bc' # 阿里云Qwen密钥
os.environ["OPENAI_BASE_URL"] = 'https://dashscope.aliyuncs.com/compatible-mode/v1'   # 例如：https://dashscope.aliyuncs.com/compatible-mode/v1


# 初始化大模型
model = ChatOpenAI(
    # model=os.getenv('DEEPSEEK_MODEL'),
    # api_key=os.getenv('DEEPSEEK_API_KEY'),
    # base_url=os.getenv('DEEPSEEK_URL')
    model = "qwen-plus",
    api_key =  os.getenv('OPENAI_API_KEY'),
    base_url = os.getenv('OPENAI_BASE_URL')
)


# Define the function that calls the model
def call_model(state: MessagesState):
    response = model.invoke(state["messages"])
    # We return a list, because this will get added to the existing list
    return {"messages": response}


# Define the two nodes we will cycle between
workflow.add_edge(START, "model")
workflow.add_node("model", call_model)


# Adding memory is straight forward in langgraph!
memory = MemorySaver()

app = workflow.compile(
    checkpointer=memory
)


# The thread id is a unique key that identifies
# this particular conversation.
# We'll just generate a random uuid here.
# This enables a single application to manage conversations among multiple users.
thread_id = uuid.uuid4()
config = {"configurable": {"thread_id": thread_id}}


input_message = HumanMessage(content="hi! I'm bob")
for event in app.stream({"messages": [input_message]}, config, stream_mode="values"):
    event["messages"][-1].pretty_print()

# Here, let's confirm that the AI remembers our name!
input_message = HumanMessage(content="what was my name?")
for event in app.stream({"messages": [input_message]}, config, stream_mode="values"):
    event["messages"][-1].pretty_print()