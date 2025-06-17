import socket
import threading
import queue
import time
import json
from typing import Optional
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage

# UDP客户端测试代码
class UDPTestClient:
    """简单的UDP测试客户端"""
    
    def __init__(self, server_host='localhost', server_port=8888):
        self.server_host = server_host
        self.server_port = server_port
    
    def send_message(self, message: str):
        """发送消息到UDP服务器"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.sendto(message.encode('utf-8'), (self.server_host, self.server_port))
            print("="*100)
            print(f"发送成功,消息是:{message}")
            
            # # 等待响应
            # sock.settimeout(120.0)
            # response, addr = sock.recvfrom(8192)
            
            # print(f"服务器响应: {response.decode('utf-8')}")
            # print("="*100)
            sock.close()
            
        except Exception as e:
            print(f"发送消息失败: {e}")

if __name__ == "__main__":

    client = UDPTestClient()
    num = 0
    messge_list =[
        "如何学习Rag?",
        "如何学习Python?",
        "计算1+1",
        "如何写代码"
    ]

    # 每隔3s发送一次udp
    while num < len(messge_list):
        client.send_message(message=messge_list[num])
        num += 1 
        time.sleep(3)