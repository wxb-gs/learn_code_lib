import streamlit as st
from langchain_ollama import ChatOllama
from custom_class import AppState
from left_panel import create_left_panel
from right_panel import crate_right_panel
from resources import get_chat_model, get_chatbot
from database import SQLManager

# 设置页面配置
st.set_page_config(
    page_title="Ollama ChatBot",
    page_icon="💬",
)

# 建立连接
state = st.session_state.get("app_state", AppState())
llm = get_chat_model()
chatbot = get_chatbot()
# 建立连接

# # 查询并展示数据, 该方法为缓存过的，需要及时清理
all_sessions = state.db_manager.get_all_sessions()

create_left_panel()

crate_right_panel()
