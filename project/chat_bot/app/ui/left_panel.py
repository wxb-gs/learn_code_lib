import streamlit as st
from .custom_class import AppState
from langchain_core.runnables import Runnable
from .resources import get_chat_model


def create_left_panel():
    state = st.session_state.get("app_state", AppState())
    llm = get_chat_model()

    css = """
<style>
    .st-emotion-cache-r90ti5{
        max-width:300px !important;
    }
<style>
"""
    st.markdown(css, unsafe_allow_html=True)

    # 你的 sidebar 内容
    with st.sidebar:
        # # 插入 logo 或标题到 sidebar 顶部
        st.markdown(
            """
            <style>
            /* 添加文字标题 */
            [data-testid="stLogoSpacer"]::before {
                content: "📊 智能助手";
                display: block;
                font-size: 20px;
                font-weight: bold;
            }
            </style>
            """,
            unsafe_allow_html=True
        )
        st.write("这里是侧边栏内容")
        st.button("按钮")
