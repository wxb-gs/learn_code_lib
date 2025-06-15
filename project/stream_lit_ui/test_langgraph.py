import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts.prompt import PromptTemplate
from langchain_ollama import ChatOllama
from langchain_core.messages import trim_messages
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, END, StateGraph, MessagesState


# ------------------ Prompt 模板 ------------------
template = """
你是一个智能问答机器人，请结合以下历史对话消息回答我的问题：
{chat_history}
问题：{question}

请提供正确、详细清晰的回答。
"""
chat_prompt_template = PromptTemplate.from_template(template)


# ------------------ 消息处理 ------------------
def process_messages(state) -> dict:
    trimmed = trim_messages(
        state["messages"],
        max_tokens=16,
        strategy="last",
        start_on="human",
        token_counter=len,
    )
    last_msg = trimmed[-1].content if trimmed else ""
    chat_history = "\n".join([m.pretty_repr() for m in trimmed[:-1]])

    prompt = chat_prompt_template.format(
        chat_history=chat_history,
        question=last_msg,
    )
    return {"messages": [HumanMessage(content=prompt)]}


# ------------------ LangGraph Agent ------------------
class ChatBot:
    def __init__(self, model_name="qwen2.5:7b"):
        self.llm = ChatOllama(model=model_name, temperature=0.7)
        self.app = self.define()

    def stream_model(self, state: MessagesState):
        for chunk in self.llm.stream(state["messages"]):
            if chunk.content:
                yield {"messages": [AIMessage(content=chunk.content)]}

    def define(self):
        graph = StateGraph(MessagesState)
        graph.add_node("before", process_messages)
        graph.add_node("model", self.stream_model)
        graph.add_edge(START, "before")
        graph.add_edge("before", "model")
        graph.add_edge("model", END)
        return graph.compile(checkpointer=MemorySaver())

    def answer_updates(self, question: str, thread_id: str = "default"):
        config = {"configurable": {"thread_id": thread_id}}
        inputs = {"messages": [HumanMessage(content=question)]}
        return self.app.stream(input=inputs, config=config, stream_mode="updates")


# ------------------ Streamlit UI ------------------

st.set_page_config(page_title="RAG 聊天机器人", layout="centered")
st.title("🧠 RAG 智能问答机器人")
st.markdown("问我任何问题，我将结合上下文为你解答！")

# 会话状态初始化
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

bot = ChatBot()

# 用户输入
question = st.chat_input("请输入你的问题...")

# 展示历史消息
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 提交新问题
if question:
    # 显示用户问题
    st.chat_message("user").markdown(question)
    st.session_state.chat_history.append({"role": "user", "content": question})

    # 显示 AI 回复框
    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_response = ""

        for update in bot.answer_updates(question, thread_id="streamlit"):
            for msg in update.get("messages", []):
                if isinstance(msg, AIMessage):
                    full_response += msg.content
                    placeholder.markdown(full_response + "▌")  # 动态输出

        placeholder.markdown(full_response)  # 移除游标
        st.session_state.chat_history.append(
            {"role": "assistant", "content": full_response})
