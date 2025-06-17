#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
from pypinyin import lazy_pinyin, Style


def chinese_to_pinyin_with_replacement_advanced(text: str):
    """
    更高级的版本：处理词语边界，避免误替换
    
    Args:
        text (str): 输入的中文文本
    
    Returns:
        str: 处理后的文本
    """
    
    # 定义同音词替换映射
    replacement_words = ["洞幺", "羊工"]
    
    # 将中文转换为拼音（不带声调）
    pinyin_list = lazy_pinyin(text, style=Style.NORMAL)
    replace_list = []
    for word in replacement_words:
        replace_list.append(lazy_pinyin(word, style=Style.NORMAL))

    # pinyin_with_spaces = ' '.join(pinyin_list)

    print("#"*50)
    print(replace_list)
    print(pinyin_list)
    # 原文本是text
    # for word in replace_list:
    len_t = len(text)
    for raw_index ,words in enumerate(replace_list):
        index = -1
        need = len(words)
        j = 0
        for i in range(0, len_t - need + 1):
            if pinyin_list[i] == words[j]:
                j += 1
            else:
                j = 0
            if j >= need:
                index = i - need + 1
                break
        if index != -1:
            # 替换
            text = text[:index] + replacement_words[raw_index] + text[index + need:]

    return text


# 示例使用
if __name__ == "__main__":
    # 测试文本
    test_texts = [
        "动摇不定的计划需要阳供普照",
        "董尧是个好人，杨公也很不错",
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

