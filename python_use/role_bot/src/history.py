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
def get_history_blocks(expand_states=None):
    session_id = "default_session"
    history_obj = get_session_history(session_id)
    messages = history_obj.messages
    if not messages:
        return [gr.Markdown("暂无历史记录。")]
    blocks = []
    if expand_states is None or len(expand_states) != len(messages):
        expand_states = [False] * len(messages)
    for i, msg in enumerate(messages):
        role = msg.type if hasattr(msg, 'type') else msg.role if hasattr(msg, 'role') else 'unknown'
        content = msg.content if hasattr(msg, 'content') else str(msg)
        if not expand_states[i] and len(content) > 80:
            display_content = content[:80] + "..."
            btn_text = "展开"
        else:
            display_content = content
            btn_text = "收起" if len(content) > 80 else ""
        blocks.append(gr.Markdown(f"**{role}**: {display_content}"))
        if btn_text:
            blocks.append(gr.Button(btn_text, elem_id=f"expand-btn-{i}"))
        blocks.append(gr.Markdown("---"))
    return blocks, expand_states

with gr.Blocks() as demo:
    with gr.Tabs():
        with gr.TabItem("聊天"):
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
            )
        with gr.TabItem("历史记录"):
            expand_states = gr.State([])
            history_column = gr.Column()
            def refresh_history(expand_states):
                blocks, states = get_history_blocks(expand_states)
                return blocks, states
            refresh_btn = gr.Button("刷新历史记录")
            refresh_btn.click(refresh_history, [expand_states], [history_column, expand_states])
            # 动态为每个按钮注册点击事件
            def make_expand_fn(idx):
                def fn(expand_states):
                    expand_states = list(expand_states) if expand_states else []
                    while len(expand_states) <= idx:
                        expand_states.append(False)
                    expand_states[idx] = not expand_states[idx]
                    blocks, states = get_history_blocks(expand_states)
                    return blocks, states
                return fn
            # 初始渲染
            blocks, states = get_history_blocks()
            history_column.render(blocks)
            expand_states.value = states
            # 由于gradio不支持动态注册按钮事件，这里仅做结构示例，实际需用gradio 4.x的事件系统或js自定义
    demo.launch()

textbox=gr.Textbox(placeholder="输入消息...", scale=7)
textbox.submit()
