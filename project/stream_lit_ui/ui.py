from langchain_ollama import ChatOllama
from langchain.schema.messages import HumanMessage
from pathlib import Path
import streamlit as st
import time
from PIL import Image
llm = ChatOllama(model="qwen2.5:7b", streaming=True)



with st.sidebar:
    with st.echo():
        st.write("This code will be printed to the sidebar.")

    with st.spinner("Loading..."):
        time.sleep(5)
    st.success("Done!")

with st.container():
    usr_img = Image.open("./icon/user.png")
    sys_img = Image.open("./icon/sys.png")
    # usr_img = st.image("./icon/user.png")
    # sys_img = st.image("./icon/sys.png")
    with st.chat_message(name='human',avatar=usr_img):
        st.markdown("你好")
    with st.chat_message(name='ai',avatar=sys_img):
        st.markdown("""# 373. 查找和最小的 K 对数字 
给定两个以 **非递减顺序排列**  的整数数组 `nums1` 和 `nums2` , 以及一个整数 `k` 。

定义一对值 `(u,v)`，其中第一个元素来自 `nums1`，第二个元素来自 `nums2` 。

请找到和最小的 `k` 个数对 `(u_1,v_1)`,  `(u_2,v_2)`  \.\.\.  `(u_k,v_k)` 。

**示例 1:** 

> **输入:**  nums1 = \[1,7,11], nums2 = \[2,4,6], k = 3
> **输出:**  \[1,2],\[1,4],\[1,6]
> **解释:**  返回序列中的前 3 对数：
>      \[1,2],\[1,4],\[1,6],\[7,2],\[7,4],\[11,2],\[7,6],\[11,4],\[11,6]
> 

**示例 2:** 

> **输入:**  nums1 = \[1,1,2], nums2 = \[1,2,3], k = 2
> **输出:**  \[1,1],\[1,1]
> **解释:**  返回序列中的前 2 对数：
>      \[1,1],\[1,1],\[1,2],\[2,1],\[1,2],\[2,2],\[1,3],\[1,3],\[2,3]
> 

**提示:** 

*   `1 <= nums1.length, nums2.length <= 10^5`
*   `-10^9 <= nums1[i], nums2[i] <= 10^9`
*   `nums1` 和 `nums2` 均为 **升序排列** 
*   `1 <= k <= 10^4`
*   `k <= nums1.length * nums2.length`""")