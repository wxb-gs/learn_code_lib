from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts.prompt import PromptTemplate
from langchain_ollama import ChatOllama
from langchain_core.messages import trim_messages
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, END, StateGraph, MessagesState


# 模型输入模板
template = """
你是一个智能问答机器人，请结合以下历史对话消息回答我的问题：
{chat_history}
问题：{question}

请提供正确、详细清晰的回答。
"""
chat_prompt_template = PromptTemplate.from_template(template)

MODEL_RUN = "model_run"
BEFORE_MODEL_PROCESS = "before_model_process"


# 处理消息，构建prompt
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


# ChatBot 主体
class ChatBot:
    def __init__(self, model_name="qwen2.5:7b"):
        self.llm = ChatOllama(model=model_name, temperature=0.7)
        self.app = self.define()

    def stream_model(self, state: MessagesState):
        for chunk in self.llm.stream(state["messages"]):
            # if chunk.content:
            yield {"messages": [AIMessage(content=chunk.content)]}

    def define(self):
        graph = (
            StateGraph(MessagesState)
            .add_node(BEFORE_MODEL_PROCESS, process_messages)
            .add_node(MODEL_RUN, self.stream_model)
            .add_edge(START, BEFORE_MODEL_PROCESS)
            .add_edge(BEFORE_MODEL_PROCESS, MODEL_RUN)
            .add_edge(MODEL_RUN, END)
        )
        memory_saver = MemorySaver()
        return graph.compile(checkpointer=memory_saver)

    def answer_updates(self, question: str, thread_id: str = "default"):
        config = {"configurable": {"thread_id": thread_id}}
        inputs = {"messages": [HumanMessage(content=question)]}
        return self.app.stream(input=inputs, config=config, stream_mode=["values"])


# 测试：以更新模式流式输出
if __name__ == "__main__":
    bot = ChatBot()
    print("回答开始：")

    for update in bot.answer_updates("如何学习RAG", thread_id="456"):
        # update 是类似 {'messages': [AIMessage(...)]} 的增量
        # messages = update.get("messages", [])
        print(update)
        # for msg in messages:
        #     if isinstance(msg, AIMessage):
        #         print(msg.content, end="", flush=True)
