import streamlit as st
from sqlalchemy import create_engine, text, Column, String, Boolean, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
# 修改点1：使用新的声明式基类
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Mapped, mapped_column
import uuid
from datetime import datetime
from langchain.schema import HumanMessage, AIMessage, BaseMessage
import json

# 封装聊天会话数据的类


class ChatData:
    def __init__(self, session_id, name, create_time, last_update, messages: list[BaseMessage], wake_words, smart_mode):
        self.id = session_id
        self.name = name
        self.create_time = create_time
        self.last_update = last_update
        self.messages = messages
        self.wake_words = wake_words
        self.smart_mode = smart_mode

    def to_dict(self):
        """将ChatData对象转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'create_time': self.create_time,
            'last_update': self.last_update,
            'messages': self.messages,
            'wake_words': self.wake_words,
            'smart_mode': self.smart_mode
        }

# 声明基类 (SQLAlchemy 2.0 新语法)


class Base(DeclarativeBase):  # 修改点2：继承DeclarativeBase而不是使用declarative_base()
    pass

# 定义模型类


class ChatSession(Base):
    __tablename__ = 'chat_sessions'

    # 使用新的ORM映射语法
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)  # 修改点3
    name: Mapped[str] = mapped_column(String)
    create_time: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now)
    last_update: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, onupdate=datetime.now  # 修改点4：移除多余的括号
    )
    messages: Mapped[str] = mapped_column(Text)  # 存储为JSON字符串
    wake_words: Mapped[str] = mapped_column(Text)  # 存储为JSON字符串
    smart_mode: Mapped[bool] = mapped_column(Boolean)

    def to_dict(self):
        return {
            'id': str(self.id),
            'name': self.name,
            'create_time': self.create_time,
            'last_update': self.last_update,
            'messages': self._deserialize_messages(),
            'wake_words': json.loads(self.wake_words) if self.wake_words else [],
            'smart_mode': self.smart_mode
        }

    def to_chat_data(self):
        """将会话对象转换为ChatData对象"""
        return ChatData(
            session_id=str(self.id),
            name=self.name,
            create_time=self.create_time,
            last_update=self.last_update,
            messages=self._deserialize_messages(),
            wake_words=json.loads(self.wake_words) if self.wake_words else [],
            smart_mode=self.smart_mode
        )

    def _deserialize_messages(self):
        if not self.messages:
            return []
        messages = json.loads(self.messages)
        return [
            HumanMessage(content=msg['content']) if msg['type'] == 'human'
            else AIMessage(content=msg['content'])
            for msg in messages
        ]

# 数据库管理类
class SQLManager:
    def __init__(self):
        self.conn = st.connection("session_db", type="sql")
        self.engine = self.conn.engine
        self.create_table()

        # 使用缓存优化数据库连接
        self.session = self._create_session()  # 修改点5：使用缓存创建会话

    @st.cache_resource  # 修改点6：添加缓存资源装饰器[2,3](@ref)
    def _create_session(_self):
        """创建并缓存数据库会话"""
        Session = sessionmaker(bind=_self.engine)
        return Session()

    def create_table(self):
        """创建数据表（如果不存在）"""
        Base.metadata.create_all(self.engine)

    def add_session(self, name, messages=None, wake_words=None, smart_mode=False):
        """添加新会话"""
        messages = messages or []
        wake_words = wake_words or []

        serialized_messages = [
            {'type': 'human', 'content': msg.content} if isinstance(msg, HumanMessage)
            else {'type': 'ai', 'content': msg.content}
            for msg in messages
        ]

        new_session = ChatSession(
            name=name,
            messages=json.dumps(serialized_messages),
            wake_words=json.dumps(wake_words),
            smart_mode=smart_mode
        )

        self.session.add(new_session)
        self.session.commit()
        self.get_all_sessions().clear()
        return str(new_session.id)  # 修改点7：返回字符串格式ID

    @st.cache_data(ttl=300)  # 修改点8：缓存查询结果5分钟[2,3](@ref)
    def get_all_sessions(_self):
        """获取所有会话（带缓存）"""
        sessions = _self.session.query(ChatSession).all()
        return [session.to_chat_data() for session in sessions]

    def get_session(self, session_id):
        """获取单个会话"""
        session = self.session.query(ChatSession).get(
            uuid.UUID(session_id))  # 修改点9：转换UUID格式
        return session.to_dict() if session else None

    def update_session(self, session_id, **kwargs):
        """更新会话信息"""
        session = self.session.query(ChatSession).get(uuid.UUID(session_id))
        if not session:
            return False

        if 'name' in kwargs:
            session.name = kwargs['name']
        if 'messages' in kwargs:
            messages = kwargs['messages']
            serialized_messages = [
                {'type': 'human', 'content': msg.content} if isinstance(msg, HumanMessage)
                else {'type': 'ai', 'content': msg.content}
                for msg in messages
            ]
            session.messages = json.dumps(serialized_messages)
        if 'wake_words' in kwargs:
            session.wake_words = json.dumps(kwargs['wake_words'])
        if 'smart_mode' in kwargs:
            session.smart_mode = kwargs['smart_mode']

        session.last_update = datetime.now()
        self.session.commit()

        # 在更新会话的时候清除未更新的缓存
        self.get_all_sessions().clear()
        return True

    def delete_session(self, session_id):
        """删除会话"""
        session = self.session.query(ChatSession).get(uuid.UUID(session_id))
        if session:
            self.session.delete(session)
            self.session.commit()

            self.get_all_sessions().clear()
            return True
        return False

    def add_message(self, session_id, messages: list[BaseMessage]):
        """添加消息到会话"""
        session = self.session.query(ChatSession).get(uuid.UUID(session_id))
        if not session:
            return False

        session_messages = session._deserialize_messages()
        session_messages.extend(messages)

        serialized_messages = [
            {'type': 'human', 'content': msg.content} if isinstance(msg, HumanMessage)
            else {'type': 'ai', 'content': msg.content}
            for msg in session_messages
        ]
        session.messages = json.dumps(serialized_messages)
        session.last_update = datetime.now()

        self.session.commit()

        self.get_all_sessions().clear()
        return True


if __name__ == "__main__":

    # 会话状态管理
    if "db_manager" not in st.session_state:  # 修改点10：使用会话状态管理[5](@ref)
        st.session_state.db_manager = SQLManager()
    st.write("数据库连接已建立")
    if st.button("插入一条随机数据"):
        str_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        new_session = {
            "name": f"新建会话 - {str_time}",
        }
        st.markdown(new_session)
        st.session_state.db_manager.add_session(
            name=new_session["name"]
        )
