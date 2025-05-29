import gradio as gr
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
# 1. 构建基础链（保持不变）
llm = ChatOllama(model="Qwen2.5-7B-Instruct:latest")
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个AI助手"),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{input}")
])
chain = prompt | llm

# 2. 初始化消息历史管理（保持不变）
store = {}
def get_session_history(session_id: str) -> ChatMessageHistory:
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]

# 3. 包装可运行对象（保持不变）
runnable = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key="input",
    history_messages_key="history"
)

# 4. 响应生成函数（保持不变）
def respond(message: str, history: list):
    session_id = "default_session"
    response = ""
    for chunk in runnable.stream(
        {"input": message},
        config={"configurable": {"session_id": session_id}}
    ):
        response += chunk.content
        yield [{"role": "user", "content": message},
               {"role": "assistant", "content": response}]

# 5. 构建界面（关键修改部分）
gr.ChatInterface(
    respond,
    chatbot=gr.Chatbot(type="messages", elem_id="custom-chatbot"),
    textbox=gr.Textbox(placeholder="输入消息...", scale=7),
    examples=["你好！", "如何学习AI？"],
    title="智能助手",
    css="""r
    #custom-chatbot{
        height: 600px !important;
    }
    #custom-chatbot .wrapper.svelte-g3p8na {
        height: auto !important;  /* 内部自适应高度 */
        background: #18181B;
    }
    """
).launch()

textbox=gr.Textbox(placeholder="输入消息...", scale=7)
textbox.submit()
