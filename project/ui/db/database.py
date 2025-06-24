import sqlite3
import json
import uuid
from datetime import datetime
import os


class ConversationDatabase:
    """对话数据库管理类"""

    def __init__(self, db_path="conversations.db"):
        """
        初始化数据库连接

        Args:
            db_path (str): 数据库文件路径
        """
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """
        初始化数据库，创建表结构
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # 创建对话表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS conversations (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    create_time REAL NOT NULL,
                    last_used_time REAL NOT NULL,
                    wake_words TEXT NOT NULL,
                    smart_mode BOOLEAN DEFAULT FALSE,
                    messages TEXT DEFAULT '[]',
                    modified BOOLEAN DEFAULT FALSE,
                    last_updated TEXT,
                    time_threshold REAL DEFAULT 5.0
                )
            ''')

            # 检查是否需要添加 time_threshold 列（用于数据库升级）
            cursor.execute("PRAGMA table_info(conversations)")
            columns = [column[1] for column in cursor.fetchall()]
            
            if 'time_threshold' not in columns:
                cursor.execute('''
                    ALTER TABLE conversations 
                    ADD COLUMN time_threshold REAL DEFAULT 5.0
                ''')
                print("已添加 time_threshold 列到现有数据库")

            conn.commit()
            conn.close()
            print(f"数据库初始化成功: {self.db_path}")

        except Exception as e:
            print(f"数据库初始化失败: {e}")

    def generate_uuid(self):
        """
        生成UUID作为对话ID

        Returns:
            str: UUID字符串
        """
        return str(uuid.uuid4())

    def save_conversation(self, conversation_data):
        """
        保存或更新对话到数据库

        Args:
            conversation_data (dict): 对话数据

        Returns:
            bool: 保存是否成功
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # 确保ID存在
            if 'id' not in conversation_data or not conversation_data['id']:
                conversation_data['id'] = self.generate_uuid()

            # 转换wake_words为JSON字符串
            wake_words_json = json.dumps(conversation_data.get('wake_words', []))
            messages_json = json.dumps(conversation_data.get('messages', []))

            # 更新最后修改时间
            conversation_data['last_updated'] = datetime.now().isoformat()

            # 使用REPLACE INTO实现插入或更新
            cursor.execute('''
                REPLACE INTO conversations 
                (id, name, create_time, last_used_time, wake_words, smart_mode, 
                 messages, modified, last_updated, time_threshold)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                conversation_data['id'],
                conversation_data.get('name', '未知对话'),
                conversation_data.get('create_time', datetime.now().timestamp()),
                conversation_data.get('last_used_time', datetime.now().timestamp()),
                wake_words_json,
                conversation_data.get('smart_mode', False),
                messages_json,
                conversation_data.get('modified', False),
                conversation_data['last_updated'],
                conversation_data.get('time_threshold', 5.0)
            ))

            conn.commit()
            conn.close()
            print(f"保存对话成功: {conversation_data.get('name', '未知对话')}")
            return True

        except Exception as e:
            print(f"保存对话失败: {e}")
            return False

    def load_conversation(self, conversation_id):
        """
        根据ID加载单个对话

        Args:
            conversation_id (str): 对话ID

        Returns:
            dict or None: 对话数据，如果不存在返回None
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                SELECT id, name, create_time, last_used_time, wake_words, 
                       smart_mode, messages, modified, last_updated, time_threshold
                FROM conversations 
                WHERE id = ?
            ''', (conversation_id,))

            row = cursor.fetchone()
            conn.close()

            if row:
                return self._row_to_dict(row)
            else:
                print(f"未找到对话: {conversation_id}")
                return None

        except Exception as e:
            print(f"加载对话失败: {e}")
            return None

    def load_all_conversations(self):
        """
        加载所有对话

        Returns:
            list: 对话列表
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                SELECT id, name, create_time, last_used_time, wake_words, 
                       smart_mode, messages, modified, last_updated, time_threshold
                FROM conversations 
                ORDER BY create_time DESC
            ''')

            rows = cursor.fetchall()
            conn.close()

            conversations = []
            for row in rows:
                conversations.append(self._row_to_dict(row))

            print(f"加载所有对话成功，共 {len(conversations)} 个")
            return conversations

        except Exception as e:
            print(f"加载所有对话失败: {e}")
            return []

    def delete_conversation(self, conversation_id):
        """
        删除对话

        Args:
            conversation_id (str): 对话ID

        Returns:
            bool: 删除是否成功
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # 先检查对话是否存在
            cursor.execute('SELECT name FROM conversations WHERE id = ?', (conversation_id,))
            row = cursor.fetchone()

            if row:
                conversation_name = row[0]
                cursor.execute('DELETE FROM conversations WHERE id = ?', (conversation_id,))
                conn.commit()
                conn.close()
                print(f"删除对话成功: {conversation_name}")
                return True
            else:
                conn.close()
                print(f"要删除的对话不存在: {conversation_id}")
                return False

        except Exception as e:
            print(f"删除对话失败: {e}")
            return False

    def update_conversation_messages(self, conversation_id, messages):
        """
        更新对话的消息记录

        Args:
            conversation_id (str): 对话ID
            messages (list): 消息列表

        Returns:
            bool: 更新是否成功
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            messages_json = json.dumps(messages)
            current_time = datetime.now().timestamp()

            cursor.execute('''
                UPDATE conversations 
                SET messages = ?, last_used_time = ?, last_updated = ?, modified = TRUE
                WHERE id = ?
            ''', (messages_json, current_time, datetime.now().isoformat(), conversation_id))

            if cursor.rowcount > 0:
                conn.commit()
                conn.close()
                print(f"更新对话消息成功: {conversation_id}")
                return True
            else:
                conn.close()
                print(f"对话不存在，无法更新: {conversation_id}")
                return False

        except Exception as e:
            print(f"更新对话消息失败: {e}")
            return False

    def update_conversation_settings(self, conversation_id, name=None, wake_words=None, smart_mode=None, time_threshold=None):
        """
        更新对话的设置信息（简化版）

        Args:
            conversation_id (str): 对话ID
            name (str, optional): 对话名称
            wake_words (list, optional): 唤醒词列表
            smart_mode (bool, optional): 智能模式
            time_threshold (float, optional): 时间阈值

        Returns:
            bool: 更新是否成功
        """
        try:
            # 先获取当前对话数据
            current_data = self.load_conversation(conversation_id)
            if not current_data:
                print(f"对话不存在，无法更新: {conversation_id}")
                return False

            # 更新指定字段，如果参数为None则保持原值
            if name is not None:
                current_data['name'] = name
            if wake_words is not None:
                current_data['wake_words'] = wake_words
            if smart_mode is not None:
                current_data['smart_mode'] = smart_mode
            if time_threshold is not None:
                current_data['time_threshold'] = float(time_threshold)

            # 标记为已修改
            current_data['modified'] = True
            current_data['last_used_time'] = datetime.now().timestamp()

            # 使用现有的save_conversation方法保存
            if self.save_conversation(current_data):
                print(f"更新对话设置成功: {conversation_id}")
                return True
            else:
                print(f"保存更新失败: {conversation_id}")
                return False

        except Exception as e:
            print(f"更新对话设置失败: {e}")
            return False

    def update_time_threshold(self, conversation_id, time_threshold):
        """
        更新对话的时间阈值

        Args:
            conversation_id (str): 对话ID
            time_threshold (float): 时间阈值

        Returns:
            bool: 更新是否成功
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                UPDATE conversations 
                SET time_threshold = ?, last_updated = ?, modified = TRUE
                WHERE id = ?
            ''', (float(time_threshold), datetime.now().isoformat(), conversation_id))

            if cursor.rowcount > 0:
                conn.commit()
                conn.close()
                print(f"更新时间阈值成功: {conversation_id} -> {time_threshold}")
                return True
            else:
                conn.close()
                print(f"对话不存在，无法更新时间阈值: {conversation_id}")
                return False

        except Exception as e:
            print(f"更新时间阈值失败: {e}")
            return False

    def update_last_used_time(self, conversation_id):
        """
        更新对话的最后使用时间

        Args:
            conversation_id (str): 对话ID

        Returns:
            bool: 更新是否成功
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            current_time = datetime.now().timestamp()
            cursor.execute('''
                UPDATE conversations 
                SET last_used_time = ?
                WHERE id = ?
            ''', (current_time, conversation_id))

            if cursor.rowcount > 0:
                conn.commit()
                conn.close()
                return True
            else:
                conn.close()
                return False

        except Exception as e:
            print(f"更新最后使用时间失败: {e}")
            return False

    def create_new_conversation(self, name=None, wake_words=None, smart_mode=False, time_threshold=5.0):
        """
        创建新对话

        Args:
            name (str): 对话名称，如果为None则自动生成
            wake_words (list): 唤醒词列表
            smart_mode (bool): 是否启用智能模式
            time_threshold (float): 时间阈值，默认5.0秒

        Returns:
            dict: 新创建的对话数据
        """
        current_timestamp = datetime.now().timestamp()
        current_time = datetime.now().strftime("%m-%d %H:%M:%S")

        if name is None:
            name = f"会话 - {current_time}"

        if wake_words is None:
            wake_words = ['小爱同学', '豆包']

        new_conversation = {
            "id": self.generate_uuid(),
            "name": name,
            "create_time": current_timestamp,
            "last_used_time": current_timestamp,
            "wake_words": wake_words,
            "smart_mode": smart_mode,
            "messages": [],
            "modified": False,
            "time_threshold": float(time_threshold)
        }

        if self.save_conversation(new_conversation):
            print(f"创建新对话成功: {name}")
            return new_conversation
        else:
            print(f"创建新对话失败: {name}")
            return None

    def search_conversations(self, keyword):
        """
        搜索对话（根据名称或消息内容）

        Args:
            keyword (str): 搜索关键词

        Returns:
            list: 匹配的对话列表
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # 搜索名称或消息内容包含关键词的对话
            cursor.execute('''
                SELECT id, name, create_time, last_used_time, wake_words, 
                       smart_mode, messages, modified, last_updated, time_threshold
                FROM conversations 
                WHERE name LIKE ? OR messages LIKE ?
                ORDER BY last_used_time DESC
            ''', (f'%{keyword}%', f'%{keyword}%'))

            rows = cursor.fetchall()
            conn.close()

            conversations = []
            for row in rows:
                conversations.append(self._row_to_dict(row))

            print(f"搜索对话成功，找到 {len(conversations)} 个匹配结果")
            return conversations

        except Exception as e:
            print(f"搜索对话失败: {e}")
            return []

    def get_conversation_count(self):
        """
        获取对话总数

        Returns:
            int: 对话总数
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('SELECT COUNT(*) FROM conversations')
            count = cursor.fetchone()[0]
            conn.close()

            return count

        except Exception as e:
            print(f"获取对话总数失败: {e}")
            return 0

    def get_conversations_by_threshold(self, min_threshold=None, max_threshold=None):
        """
        根据时间阈值范围获取对话

        Args:
            min_threshold (float, optional): 最小时间阈值
            max_threshold (float, optional): 最大时间阈值

        Returns:
            list: 符合条件的对话列表
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # 构建查询条件
            where_conditions = []
            params = []

            if min_threshold is not None:
                where_conditions.append("time_threshold >= ?")
                params.append(min_threshold)

            if max_threshold is not None:
                where_conditions.append("time_threshold <= ?")
                params.append(max_threshold)

            where_clause = ""
            if where_conditions:
                where_clause = "WHERE " + " AND ".join(where_conditions)

            query = f'''
                SELECT id, name, create_time, last_used_time, wake_words, 
                       smart_mode, messages, modified, last_updated, time_threshold
                FROM conversations 
                {where_clause}
                ORDER BY time_threshold ASC
            '''

            cursor.execute(query, params)
            rows = cursor.fetchall()
            conn.close()

            conversations = []
            for row in rows:
                conversations.append(self._row_to_dict(row))

            print(f"根据时间阈值查询成功，找到 {len(conversations)} 个对话")
            return conversations

        except Exception as e:
            print(f"根据时间阈值查询失败: {e}")
            return []

    def _row_to_dict(self, row):
        """
        将数据库行转换为字典格式

        Args:
            row (tuple): 数据库行数据

        Returns:
            dict: 对话字典数据
        """
        try:
            return {
                'id': row[0],
                'name': row[1],
                'create_time': row[2],
                'last_used_time': row[3],
                'wake_words': json.loads(row[4]) if row[4] else [],
                'smart_mode': bool(row[5]),
                'messages': json.loads(row[6]) if row[6] else [],
                'modified': bool(row[7]) if row[7] is not None else False,
                'last_updated': row[8],
                'time_threshold': float(row[9]) if len(row) > 9 and row[9] is not None else 5.0
            }
        except Exception as e:
            print(f"转换数据行失败: {e}")
            # 返回基本结构，避免程序崩溃
            return {
                'id': row[0] if len(row) > 0 else self.generate_uuid(),
                'name': row[1] if len(row) > 1 else '未知对话',
                'create_time': row[2] if len(row) > 2 else datetime.now().timestamp(),
                'last_used_time': row[3] if len(row) > 3 else datetime.now().timestamp(),
                'wake_words': [],
                'smart_mode': False,
                'messages': [],
                'modified': False,
                'last_updated': datetime.now().isoformat(),
                'time_threshold': 5.0
            }

    def close(self):
        """
        关闭数据库连接（清理资源）
        """
        # SQLite连接在每个操作后都会关闭，这里主要用于接口统一
        print("数据库操作完成")

    def backup_database(self, backup_path):
        """
        备份数据库

        Args:
            backup_path (str): 备份文件路径

        Returns:
            bool: 备份是否成功
        """
        try:
            import shutil
            shutil.copy2(self.db_path, backup_path)
            print(f"数据库备份成功: {backup_path}")
            return True
        except Exception as e:
            print(f"数据库备份失败: {e}")
            return False

    def restore_database(self, backup_path):
        """
        从备份恢复数据库

        Args:
            backup_path (str): 备份文件路径

        Returns:
            bool: 恢复是否成功
        """
        try:
            import shutil
            if os.path.exists(backup_path):
                shutil.copy2(backup_path, self.db_path)
                print(f"数据库恢复成功: {backup_path}")
                return True
            else:
                print(f"备份文件不存在: {backup_path}")
                return False
        except Exception as e:
            print(f"数据库恢复失败: {e}")
            return False

    def clear_all_conversations(self):
        """
        清空所有对话数据（保留表结构）

        Returns:
            bool: 清空是否成功
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # 删除前先备份
            self.clear_conversations_with_backup()

            # 删除所有对话记录
            cursor.execute('DELETE FROM conversations')

            # 重置自增ID（如果有的话）
            cursor.execute('DELETE FROM sqlite_sequence WHERE name="conversations"')

            conn.commit()
            conn.close()

            print("所有对话数据清空成功")
            return True

        except Exception as e:
            print(f"清空对话数据失败: {e}")
            return False

    def clear_conversations_with_backup(self, backup_path=None):
        """
        清空对话数据前先备份

        Args:
            backup_path (str): 备份路径，如果为None则自动生成

        Returns:
            bool: 操作是否成功
        """
        try:
            # 生成备份路径
            if backup_path is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = f"conversations_backup_{timestamp}.db"

            # 先备份
            if self.backup_database(backup_path):
                # 备份成功后清空
                if self.clear_all_conversations():
                    print(f"数据已备份到 {backup_path} 并清空成功")
                    return True
                else:
                    print("备份成功但清空失败")
                    return False
            else:
                print("备份失败，取消清空操作")
                return False

        except Exception as e:
            print(f"备份并清空失败: {e}")
            return False