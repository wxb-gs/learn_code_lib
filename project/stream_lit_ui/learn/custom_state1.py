import streamlit as st


class AppState:
    counter: int
    items: list[str]

    def __init__(self):
        # 初始化逻辑（仅首次执行）
        if not hasattr(st.session_state, "app_state"):
            st.session_state.app_state = self
            self.counter = 0
            self.items = []


# 获取状态实例
state = st.session_state.get("app_state", AppState())

# 操作（IDE识别counter为int，items为list）
if st.button("Increment"):
    state.counter += 1  # ✅ IDE支持int运算
    state.items.append(f"Item{state.counter}")  # ✅ IDE提示list.append

st.write(state.counter)
st.write(state.items)
