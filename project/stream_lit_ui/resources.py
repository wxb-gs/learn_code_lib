import streamlit as st
from langchain_ollama import ChatOllama
from chatbot import ChatBot


@st.cache_resource
def get_chat_model():
    return ChatOllama(
        model="qwen2.5:7b"
    )


@st.cache_resource
def get_chatbot():
    return ChatBot()
