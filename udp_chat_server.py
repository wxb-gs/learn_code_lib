import socket
import threading
import queue
import time
import json
from typing import Optional
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage

class UDPQueueChatSystem:
    def __init__(self, udp_host='localhost', udp_port=8888, ollama_host='localhost', ollama_port=11434, model='qwen2.5:7b'):
        """
        初始化UDP队列聊天系统
        
        Args:
            udp_host: UDP服务器主机地址
            udp_port: UDP服务器端口
            ollama_host: Ollama服务器主机地址  
            ollama_port: Ollama服务器端口
            model: 使用的Ollama模型名称
        """
        self.udp_host = udp_host
        self.udp_port = udp_port
        
        # 初始化ChatOllama
        self.chat_ollama = ChatOllama(
            model=model,
            base_url=f"http://{ollama_host}:{ollama_port}"
        )
        
        # 创建数据队列
        self.data_queue = queue.Queue()
        
        # 创建UDP socket
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_socket.bind((self.udp_host, self.udp_port))
        
        # 控制线程运行的标志
        self.running = False
        
        # 线程对象
        self.udp_thread = None
        self.processor_thread = None
        
        print(f"UDP服务器初始化完成: {self.udp_host}:{self.udp_port}")
        print(f"ChatOllama模型: {model}")
        print(f"Ollama服务器: http://{ollama_host}:{ollama_port}")
    
    def start(self):
        """启动系统"""
        self.running = True
        
        # 启动UDP接收线程
        self.udp_thread = threading.Thread(target=self._udp_receiver, daemon=True)
        self.udp_thread.start()
        
        # 启动数据处理线程
        self.processor_thread = threading.Thread(target=self._data_processor, daemon=True)
        self.processor_thread.start()
        
        print("系统启动完成！")
        print("UDP接收线程和数据处理线程已启动")
    
    def stop(self):
        """停止系统"""
        self.running = False
        
        # 关闭UDP socket
        if self.udp_socket:
            self.udp_socket.close()
        
        print("系统已停止")
    
    def _udp_receiver(self):
        """UDP数据接收线程"""
        print("UDP接收线程启动，等待数据...")
        
        while self.running:
            try:
                # 设置超时，避免阻塞
                self.udp_socket.settimeout(1.0)
                
                # 接收UDP数据
                data, addr = self.udp_socket.recvfrom(1024)
                
                # 解码数据
                message = data.decode('utf-8')
                
                # 将数据放入队列
                self.data_queue.put({
                    'message': message,
                    'sender': addr,
                    'timestamp': time.time()
                })
                
                print(f"收到UDP数据来自 {addr}: {message}")
                
            except socket.timeout:
                # 超时是正常的，继续循环
                continue
            except Exception as e:
                if self.running:
                    print(f"UDP接收错误: {e}")
                break
    
    def _data_processor(self):
        """数据处理线程"""
        print("数据处理线程启动，监听队列...")
        
        while self.running:
            try:
                # 从队列获取数据，设置超时避免阻塞
                data_item = self.data_queue.get(timeout=1.0)
                
                print(f"处理队列数据: {data_item['message']}")
                
                # 调用ChatOllama处理数据
                response = self._call_chat_ollama(data_item['message'])
                
                if response:
                    print(f"ChatOllama响应: {response}")
                    
                    # # 可选：将响应发送回UDP客户端
                    # self._send_udp_response(response, data_item['sender'])
                
                # 标记任务完成
                self.data_queue.task_done()
                
            except queue.Empty:
                # 队列为空是正常的，继续循环
                continue
            except Exception as e:
                print(f"数据处理错误: {e}")
    
    def _call_chat_ollama(self, message: str) -> Optional[str]:
        """
        调用ChatOllama处理消息
        
        Args:
            message: 要发送给ChatOllama的消息
            
        Returns:
            ChatOllama的响应文本
        """
        try:
            print(f"发送请求到ChatOllama: {message}")
            
            # 创建HumanMessage对象
            human_message = HumanMessage(content=message)
            
            # 调用ChatOllama
            response = self.chat_ollama.invoke([human_message])
            
            # 提取响应内容
            response_text = response.content
            
            print(f"ChatOllama响应长度: {len(response_text)} 字符")
            
            return response_text
                
        except Exception as e:
            print(f"ChatOllama调用错误: {e}")
            return None
    
    def _send_udp_response(self, response: str, client_addr):
        """
        将响应发送回UDP客户端
        
        Args:
            response: 响应消息
            client_addr: 客户端地址
        """
        try:
            response_data = response.encode('utf-8')
            self.udp_socket.sendto(response_data, client_addr)
            print(f"响应已发送到 {client_addr}")
        except Exception as e:
            print(f"发送UDP响应失败: {e}")
    
    def get_queue_size(self) -> int:
        """获取当前队列大小"""
        return self.data_queue.qsize()
    
    def is_running(self) -> bool:
        """检查系统是否运行中"""
        return self.running


# 使用示例
if __name__ == "__main__":
    # 创建系统实例
    system = UDPQueueChatSystem(
        udp_host='localhost',
        udp_port=8888,
        ollama_host='localhost',
        ollama_port=11434,
        model='qwen2.5:7b'  # 可以更改为其他模型如 'mistral', 'codellama' 等
    )
    
    try:
        # 启动系统
        system.start()
        
        print("\n系统运行中...")
        print("你可以使用UDP客户端发送消息到 localhost:8888")
        print("按 Ctrl+C 停止系统\n")
        
        # 保持主线程运行
        while True:
            time.sleep(1)
            
            # 显示队列状态
            queue_size = system.get_queue_size()
            if queue_size > 0:
                print(f"当前队列大小: {queue_size}")
                
    except KeyboardInterrupt:
        print("\n收到停止信号...")
        system.stop()
        print("系统已关闭")

        # xxx