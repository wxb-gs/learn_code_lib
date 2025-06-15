from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts.prompt import PromptTemplate
from langchain_ollama import ChatOllama
from langchain_core.messages import trim_messages, BaseMessage

HumanMessage(content="你好啊").pretty_print()
