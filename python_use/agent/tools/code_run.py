from langchain_core.tools import tool 
from langchain_experimental.utilities import PythonREPL
from langchain_core.runnables import RunnableLambda, RunnableConfig
from typing import Any, Dict

@tool
def python_execute_tool(code: str):
    """安全执行Python代码并捕获输出的工具"""
    repl = PythonREPL()
    try:
        # 执行代码并获取输出
        output = repl.run(code)
        return {
            "status": "success",
            "output": output,
            "error": None
        }
    except Exception as e:
        return {
            "status": "error",
            "output": None,
            "error": f"{type(e).__name__}: {str(e)}"
        }


# 使用示例
if __name__ == "__main__":
    
    # 成功案例
    success_code = {"code": "print('Hello, World!')"}
    print("成功执行结果:", python_execute_tool(success_code))
    
    # 错误案例
    error_code = {"code": "print(undefined_variable)"}
    print("错误执行结果:", python_execute_tool(error_code))