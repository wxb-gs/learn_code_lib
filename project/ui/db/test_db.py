#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用示例：展示如何使用基于数据库的会话管理系统
"""

import sys
from database import ConversationDatabase
from datetime import datetime

def main():
    """主函数：演示数据库操作"""
    
    # 初始化数据库
    print("=== 初始化数据库 ===")
    db = ConversationDatabase("test_conversations.db")
    
    # 创建示例对话
    print("\n=== 创建示例对话 ===")
    
    # 创建学习伙伴对话
    learning_partner = db.create_new_conversation(
        name="学习伙伴",
        wake_words=['学习', '知识', '教学'],
        smart_mode=True
    )
    print(f"创建学习伙伴对话: {learning_partner['id']}")
    
    # 创建生活助手对话
    life_assistant = db.create_new_conversation(
        name="生活助手",
        wake_words=['生活', '建议', '推荐'],
        smart_mode=False
    )
    print(f"创建生活助手对话: {life_assistant['id']}")
    
    # 添加消息到学习伙伴对话
    print("\n=== 添加消息 ===")
    learning_messages = [
        {"role": "user", "content": "你好，我想学习Python编程"},
        {"role": "assistant", "content": "你好！我很乐意帮助你学习Python编程。Python是一门非常适合初学者的编程语言..."},
        {"role": "user", "content": "请推荐一些学习资源"},
        {"role": "assistant", "content": "我推荐以下学习资源：\n1. 官方文档\n2. 廖雪峰的Python教程\n3. Python Crash Course书籍..."}
    ]
    
    # 更新对话消息
    db.update_conversation_messages(learning_partner['id'], learning_messages)
    
    # 添加消息到生活助手对话
    life_messages = [
        {"role": "user", "content": "推荐一些健康的早餐"},
        {"role": "assistant", "content": "这里有一些健康早餐的推荐：\n1. 燕麦片配水果\n2. 全麦面包配鸡蛋\n3. 酸奶配坚果..."}
    ]
    
    db.update_conversation_messages(life_assistant['id'], life_messages)
    
    # 查看所有对话
    print("\n=== 查看所有对话 ===")
    all_conversations = db.load_all_conversations()
    for conv in all_conversations:
        print(f"ID: {conv['id']}")
        print(f"名称: {conv['name']}")
        print(f"消息数: {len(conv['messages'])}")
        print(f"智能模式: {'是' if conv['smart_mode'] else '否'}")
        print(f"唤醒词: {', '.join(conv['wake_words'])}")
        print(f"创建时间: {datetime.fromtimestamp(conv['create_time']).strftime('%Y-%m-%d %H:%M:%S')}")
        print("-" * 50)
    
    # 搜索对话
    print("\n=== 搜索对话 ===")
    search_results = db.search_conversations("Python")
    print(f"搜索'Python'找到 {len(search_results)} 个结果:")
    for conv in search_results:
        print(f"- {conv['name']}")
    
    # 获取统计信息
    print("\n=== 统计信息 ===")
    total_count = db.get_conversation_count()
    print(f"总对话数: {total_count}")
    
    # 导出对话
    print("\n=== 导出对话 ===")
    export_path = f"exported_conversation_{learning_partner['id'][:8]}.json"
    if export_conversation_to_file(db, learning_partner['id'], export_path):
        print(f"对话导出成功: {export_path}")
    
    # 备份数据库
    print("\n=== 备份数据库 ===")
    backup_path = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    if db.backup_database(backup_path):
        print(f"数据库备份成功: {backup_path}")
    
    # 演示修改对话
    print("\n=== 修改对话 ===")
    new_name = f"学习伙伴 - 已更新 {datetime.now().strftime('%H:%M')}"
    rename_conversation(db, learning_partner['id'], new_name)
    
    # 复制对话
    print("\n=== 复制对话 ===")
    duplicate_conv = duplicate_conversation(db, learning_partner['id'])
    if duplicate_conv:
        print(f"复制对话成功: {duplicate_conv['name']}")
    
    # 最终统计
    print("\n=== 最终统计 ===")
    final_count = db.get_conversation_count()
    print(f"最终对话总数: {final_count}")
    
    # 清理资源
    db.close()
    print("\n=== 演示完成 ===")

def export_conversation_to_file(db, conversation_id, export_path):
    """导出对话到文件"""
    try:
        conversation = db.load_conversation(conversation_id)
        if conversation:
            import json
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(conversation, f, ensure_ascii=False, indent=2)
            return True
        return False
    except Exception as e:
        print(f"导出失败: {e}")
        return False

def rename_conversation(db, conversation_id, new_name):
    """重命名对话"""
    try:
        conversation = db.load_conversation(conversation_id)
        if conversation:
            conversation['name'] = new_name
            conversation['last_updated'] = datetime.now().isoformat()
            return db.save_conversation(conversation)
        return False
    except Exception as e:
        print(f"重命名失败: {e}")
        return False

def duplicate_conversation(db, conversation_id):
    """复制对话"""
    try:
        original = db.load_conversation(conversation_id)
        if original:
            duplicate = original.copy()
            duplicate['id'] = db.generate_uuid()
            duplicate['name'] = f"{original['name']} - 副本"
            duplicate['create_time'] = datetime.now().timestamp()
            duplicate['last_used_time'] = datetime.now().timestamp()
            
            if db.save_conversation(duplicate):
                return duplicate
        return None
    except Exception as e:
        print(f"复制失败: {e}")
        return None

if __name__ == "__main__":
    main()