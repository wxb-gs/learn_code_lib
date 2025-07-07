import streamlit as st
from langchain_core.runnables import Runnable
from langchain.schema import HumanMessage, AIMessage
from langchain_core.prompts.prompt import PromptTemplate
from langchain_core.messages import (
    trim_messages
)
from .custom_class import AppState
from .resources import get_chat_model, get_chatbot

def crate_right_panel():
    state = st.session_state.get("app_state", AppState())
    # llm = get_chat_model()
    chatbot = get_chatbot()
    sessions = state.db_manager.get_all_sessions()
    state.chat_messages = sessions[state.current_index].messages
    seesion_id = sessions[state.current_index].id

    # 右侧消息展示
    with st.container():
        # 显示历史消息
        for message in state.chat_messages:
            if isinstance(message, AIMessage):
                with st.chat_message("assistant"):
                    st.markdown(message.content)
            else:
                with st.chat_message("user"):
                    st.markdown(message.content)

    # 处理用户输入
    if input := st.chat_input("请输入你的问题..."):
        human_message = HumanMessage(content=input)
        state.chat_messages.append(human_message)

        with st.chat_message("human"):
            st.markdown(input)
        # 流式输出响应
        with st.chat_message("ai"):
            # 生成响应
            try:
                stream_gen = chatbot.answer(
                    question=input, thread_id=seesion_id)

                # 实现流式输出
                full_response = st.write_stream(stream_gen)

                # 将AI响应添加到会话状态
                ai_message = AIMessage(content=full_response)
                state.chat_messages.append(ai_message)

                added = state.db_manager.add_message(
                    seesion_id, [human_message, ai_message])
                if not added:
                    raise Exception("数据添加失败")
            
            except Exception as e:
                error_msg = f"发生错误: {str(e)}"
                st.error(error_msg)
                state.chat_messages.append(AIMessage(content=error_msg))
