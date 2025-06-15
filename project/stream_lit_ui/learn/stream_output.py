from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, AIMessage
from pathlib import Path
import streamlit as st
import time
from PIL import Image

# 初始化模型（启用流式输出）
llm = ChatOllama(model="qwen2.5:7b", streaming=True)

# 初始化会话状态
if "messages" not in st.session_state:
    st.session_state.messages = []

# 注入自定义CSS样式
st.markdown("""
<style>
/* 用户消息样式 - 头像靠右，气泡在左 */
.st-emotion-cache-janbn0 {
    flex-direction: row-reverse;  /* 反转布局使头像在右侧 */
}
            
.st-emotion-cache-janbn0 .st-emotion-cache-1ir3vnm {
    max-width: 80%;  /* 限制气泡宽度 */
    background-color: #e6f7ff;  /* 浅蓝色背景 */
    border-radius: 15px;  /* 圆角 */
    padding: 10px 15px;  /* 内边距 */
    margin-right: 10px;  /* 与头像间距 */
    border: 1px solid #91d5ff;  /* 边框 */
}

/* AI消息样式 */
.stChatMessage.ai .stMarkdown {
    max-width: 80%;  /* 限制气泡宽度 */
    background-color: #f6ffed;  /* 浅绿色背景 */
    border-radius: 15px;  /* 圆角 */
    padding: 10px 15px;  /* 内边距 */
    margin-left: 10px;  /* 与头像间距 */
    border: 1px solid #b7eb8f;  /* 边框 */
}
</style>
            
""", unsafe_allow_html=True)

# 侧边栏设置
with st.sidebar:
    st.title("聊天设置")
    st.write("Ollama流式输出演示")

    with st.echo():
        st.write("当前模型：qwen2.5:7b")

    # 清空聊天历史按钮
    if st.button("清空对话历史"):
        st.session_state.messages = []

# 加载头像
try:
    usr_img = Image.open("./icon/user.png")
    sys_img = Image.open("./icon/sys.png")
except:
    usr_img = None
    sys_img = None

# 显示历史消息
for message in st.session_state.messages:
    with st.chat_message(name=message["role"], avatar=usr_img if message["role"] == "human" else sys_img):
        st.markdown(message["content"])

# 处理用户输入
if prompt := st.chat_input("请输入您的问题..."):
    # 添加用户消息到历史
    st.session_state.messages.append({"role": "human", "content": prompt})

    # 显示用户消息（应用自定义样式）
    with st.chat_message("human", avatar=usr_img):
        st.markdown(prompt)

    # 准备AI消息占位符
    with st.chat_message("ai", avatar=sys_img):
        message_placeholder = st.empty()
        full_response = ""

        # 创建LangChain消息格式
        # lc_messages = [HumanMessage(content=msg["content"])
        #               for msg in st.session_state.messages
        #               if msg["role"] == "human"]
        lc_messages = st.session_state.messages

        # 流式调用模型
        for chunk in llm.stream(lc_messages):
            content = chunk.content
            full_response += content
            message_placeholder.markdown(full_response + "▌")  # 添加光标效果

        # 最终更新消息（移除光标）
        message_placeholder.markdown(full_response)

    # 添加AI响应到历史
    st.session_state.messages.append({"role": "ai", "content": full_response})
