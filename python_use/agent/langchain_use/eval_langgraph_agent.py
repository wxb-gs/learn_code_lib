import uuid
from deepeval import evaluate
from deepeval.test_case import LLMTestCase
from deepeval.metrics import AnswerRelevancyMetric, HallucinationMetric

from langchain_community.callbacks.confident_callback import DeepEvalCallbackHandler
from langchain_ollama import  OllamaLLM
from langchain_core.messages import (
    HumanMessage,
)
from deepeval.models import OllamaModel
## local
from langgraph_use import app

eval_model = OllamaModel(model='qwen2.5:7b')

# 配置评估指标
metrics = [
    AnswerRelevancyMetric(threshold=0.7, model=eval_model),
    HallucinationMetric(threshold=0.8, model=eval_model),
]

# # 主要作用是用于自动评估？？
# # 正确初始化回调处理器
# callback_handler = DeepEvalCallbackHandler(metrics=metrics)


# 定义测试场景
test_cases = [
    {
        "input": "hi! I'm bob. What is my age?",
        "expected_output": "42 years old",
        "context": ["User name is Bob"],
        "description": "应正确调用工具获取年龄"
    },
    {
        "input": "do you remember my name?",
        "expected_output": "Bob",
        "context": ["上一轮对话已告知名字"],
        "description": "应记住对话上下文"
    },
    {
        "input": "what's Alice's age?",
        "expected_output": "41 years old",
        "context": ["工具默认返回41岁"],
        "description": "处理未知用户应返回默认值"
    }
]



# 评估函数
def evaluate_agent():
    test_results = []
    thread_id = uuid.uuid4()
    config = {"configurable": {"thread_id": thread_id}}
    
    for case in test_cases:
        # 运行代理
        messages = []
        input_msg = HumanMessage(content=case["input"])
        
        for event in app.stream(
            {"messages": [input_msg]}, 
            config, 
            stream_mode="values",
            # callbacks=[callback_handler]  # 集成回调
        ):
            messages = event["messages"]
        
        actual_output = messages[-1].content
        
        # 创建测试用例
        test_case = LLMTestCase(
            input=case["input"],
            actual_output=actual_output,
            expected_output=case["expected_output"],
            context=case["context"]
        )
        
        
        # 执行评估
        evaluate([test_case], metrics)
        
        # 收集结果
        result = {
            "description": case["description"],
            "input": case["input"],
            "expected": case["expected_output"],
            "actual": actual_output,
            "metrics": {m.__name__: m.score for m in metrics},
            "success": all(m.is_successful() for m in metrics)
        }
        test_results.append(result)
    
    return test_results

# 输出格式化函数
def print_results(results):
    print("="*50)
    print("LangGraph代理评估报告")
    print("="*50)
    
    for i, res in enumerate(results, 1):
        print(f"\n测试 #{i}: {res['description']}")
        print(f"输入: {res['input']}")
        print(f"预期: {res['expected']}")
        print(f"实际: {res['actual']}")
        
        print("\n评估指标:")
        for metric, score in res["metrics"].items():
            status = "✅" if score >= 0.7 else "❌"
            print(f"  - {metric}: {score:.2f} {status}")
        
        print(f"\n总体: {'通过' if res['success'] else '失败'}")

# 主执行流程
if __name__ == "__main__":
    evaluation_results = evaluate_agent()
    print_results(evaluation_results)
    
    # 生成详细报告
    print("\n" + "="*50)
    print("评估结果摘要:")
    passed = sum(1 for r in evaluation_results if r["success"])
    print(f"测试通过率: {passed}/{len(evaluation_results)} ({passed/len(evaluation_results):.0%})")