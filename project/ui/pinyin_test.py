#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
from pypinyin import lazy_pinyin, Style

def split_text_advanced(text: str):
    """
    将文本按规则分割成数组：
    - 连续的数字、英文字母、标点符号作为一块
    - 中文字符每个字符单独一块
    
    Args:
        text (str): 输入文本
    
    Returns:
        list: 分割后的文本数组
    """
    
    # 定义匹配数字、英文字母、标点符号的模式
    pattern = r'[0-9a-zA-Z!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>/?`~]+'
    
    result = []
    i = 0
    
    while i < len(text):
        # 从当前位置开始匹配
        match = re.match(pattern, text[i:])
        
        if match:
            # 找到匹配的数字/英文/标点序列
            matched_text = match.group()
            result.append(matched_text)
            i += len(matched_text)
        else:
            # 单个中文字符或其他字符
            result.append(text[i])
            i += 1
    
    return result

def chinese_to_pinyin_with_replacement_advanced(text: str):
    """
    更高级的版本：处理词语边界，避免误替换
    
    Args:
        text (str): 输入的中文文本
    
    Returns:
        str: 处理后的文本，如果出现异常则返回原始输入
    """
    
    # 保存原始输入，用于异常时返回
    original_text = text
    
    try:
        # 定义同音词替换映射
        replacement_words = ["洞幺", "羊工"]
        
        # 将中文转换为拼音（不带声调）
        text = text.replace(" ","")
        
        list_text = split_text_advanced(text)
        
        pinyin_list = lazy_pinyin(list_text, style=Style.NORMAL)
        replace_list = []
        for word in replacement_words:
            replace_list.append(lazy_pinyin(word, style=Style.NORMAL))

        print("#"*50)
        print(list_text)
        print(pinyin_list)
        print(replace_list)
      
        len_t = len(list_text)
        for raw_index ,words in enumerate(replace_list):
            index = -1
            need = len(words)
            j = 0
            for i in range(0, len_t):
                if pinyin_list[i] == words[j]:
                    j += 1
                else:
                    j = 0
                if j >= need:
                    index = i - need + 1
                    # 替换
                    list_text = [*list_text[:index] , *list(replacement_words[raw_index]) , *list_text[index + need:]]
                    j = 0
                    
        return ''.join(list_text)
        
    except Exception as e:
        # 可选：记录错误信息用于调试
        print(f"处理过程中出现错误: {e}")
        print("返回原始输入文本")
        
        # 返回原始输入
        return original_text

# 示例使用
if __name__ == "__main__":
    # 测试文本
    test_texts = [
        "0.56 栋幺 0.5洞瑶 杨工0.5氧供0。5洞幺动摇,平飞44马赫km，转向角66°，66度杨工",
        "洞幺动摇,平飞44马赫km，转向角66°，66度杨工",
        "动摇不定的计划需要阳供普照",
        "董尧是个好人，杨  公也很不错",
        "55是洞幺,四mark_fef,洞瑶 。，fefe|!!Effie四44马赫km",
        "洞穴摇摆，阳光工作"
    ]
    
    print("\n=== 高级版本 ===")
    for text in test_texts:
        result = chinese_to_pinyin_with_replacement_advanced(text)
        print(f"原文: {text}")
        print(f"结果: {result}")
        print("-" * 40)
    
    # 交互式使用
    print("\n=== 交互式测试 ===")
    while True:
        user_input = input("\n请输入中文文本 (输入'quit'退出): ")
        if user_input.lower() == 'quit':
            break
        
        result = chinese_to_pinyin_with_replacement_advanced(user_input)
        print(f"转换结果: {result}")

