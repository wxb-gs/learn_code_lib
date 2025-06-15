# 安装库：pip install git+https://github.com/code-alexander/streamlit-state
# python need > 3.12
from streamlit_state import state

# 1. 声明带类型的状态（自动初始化）
counter_state = state(key="counter", initial=0)  # State[int] 类型
items_state = state(key="items", initial=[])     # State[list] 类型

# 2. 操作时自动提示类型
current_val: int = counter_state()  # ✅ 获取值 → IDE识别int
items_state().append("Apple")       # ✅ IDE提示list方法

# 3. 类型安全的更新方式
counter_state.set(10)               # ✅ 参数类型检查（非int报错）
counter_state(lambda x: x + 1)      # ✅ IDE推断x为int
