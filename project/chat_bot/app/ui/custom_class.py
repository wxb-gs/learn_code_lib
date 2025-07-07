from ..db.database import SQLManager
import streamlit as st


class AppState:
    chat_messages: list
    chat_history: list
    db_manager: SQLManager
    current_index: int

    def __init__(self):
        if not hasattr(st.session_state, "app_state"):
            st.session_state.app_state = self
            self.chat_messages = []
            self.chat_history = []
            self.db_manager = SQLManager()
            self.current_index = 0
