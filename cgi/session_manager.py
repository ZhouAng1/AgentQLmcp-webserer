#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import uuid
import time
from typing import Dict, List

class SessionManager:
    def __init__(self, db_path="chat_sessions.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建会话表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建消息表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                role TEXT,
                content TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES sessions (session_id)
            )
        ''')
        
        # 创建用户表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                username TEXT UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def create_session(self, user_id: str = None) -> str:
        session_id = str(uuid.uuid4())
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO sessions (session_id) VALUES (?)",
            (session_id,)
        )
        
        conn.commit()
        conn.close()
        return session_id
    
    def add_message(self, session_id: str, role: str, content: str):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO messages (session_id, role, content) VALUES (?, ?, ?)",
            (session_id, role, content)
        )
        
        cursor.execute(
            "UPDATE sessions SET last_activity = CURRENT_TIMESTAMP WHERE session_id = ?",
            (session_id,)
        )
        
        conn.commit()
        conn.close()
    
    def get_conversation_history(self, session_id: str) -> List[Dict]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT role, content FROM messages WHERE session_id = ? ORDER BY timestamp",
            (session_id,)
        )
        
        messages = []
        for row in cursor.fetchall():
            messages.append({
                "role": row[0],
                "content": row[1]
            })
        
        conn.close()
        return messages
    
    def get_session_info(self, session_id: str) -> Dict:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT created_at, last_activity FROM sessions WHERE session_id = ?",
            (session_id,)
        )
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                "session_id": session_id,
                "created_at": row[0],
                "last_activity": row[1]
            }
        return None
    
    def delete_session(self, session_id: str):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 删除会话相关的所有消息
        cursor.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))
        
        # 删除会话
        cursor.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))
        
        conn.commit()
        conn.close()
    
    def cleanup_old_sessions(self, days: int = 7):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 获取要删除的会话ID
        cursor.execute(
            "SELECT session_id FROM sessions WHERE last_activity < datetime('now', '-{} days')".format(days)
        )
        
        old_sessions = cursor.fetchall()
        
        for session in old_sessions:
            session_id = session[0]
            # 删除会话相关的所有消息
            cursor.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))
        
        # 删除过期会话
        cursor.execute(
            "DELETE FROM sessions WHERE last_activity < datetime('now', '-{} days')".format(days)
        )
        
        conn.commit()
        conn.close()
        
        return len(old_sessions)
    
    def get_session_statistics(self) -> Dict:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 总会话数
        cursor.execute("SELECT COUNT(*) FROM sessions")
        total_sessions = cursor.fetchone()[0]
        
        # 活跃会话数（24小时内）
        cursor.execute(
            "SELECT COUNT(*) FROM sessions WHERE last_activity > datetime('now', '-1 day')"
        )
        active_sessions = cursor.fetchone()[0]
        
        # 总消息数
        cursor.execute("SELECT COUNT(*) FROM messages")
        total_messages = cursor.fetchone()[0]
        
        # 今日消息数
        cursor.execute(
            "SELECT COUNT(*) FROM messages WHERE timestamp > datetime('now', 'start of day')"
        )
        today_messages = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "total_sessions": total_sessions,
            "active_sessions": active_sessions,
            "total_messages": total_messages,
            "today_messages": today_messages
        }
    
    def search_messages(self, session_id: str, keyword: str) -> List[Dict]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT role, content, timestamp FROM messages WHERE session_id = ? AND content LIKE ? ORDER BY timestamp",
            (session_id, f"%{keyword}%")
        )
        
        messages = []
        for row in cursor.fetchall():
            messages.append({
                "role": row[0],
                "content": row[1],
                "timestamp": row[2]
            })
        
        conn.close()
        return messages
    
    def export_conversation(self, session_id: str) -> str:
        """导出对话为文本格式"""
        messages = self.get_conversation_history(session_id)
        
        export_text = f"Conversation Export - Session: {session_id}\n"
        export_text += "=" * 50 + "\n\n"
        
        for msg in messages:
            role = "User" if msg["role"] == "user" else "AI"
            export_text += f"{role}: {msg['content']}\n\n"
        
        return export_text

# 测试函数
if __name__ == "__main__":
    # 测试会话管理器
    manager = SessionManager("test_sessions.db")
    
    # 创建会话
    session_id = manager.create_session()
    print(f"Created session: {session_id}")
    
    # 添加消息
    manager.add_message(session_id, "user", "Hello, AI!")
    manager.add_message(session_id, "assistant", "Hello! How can I help you today?")
    
    # 获取历史
    history = manager.get_conversation_history(session_id)
    print("Conversation history:")
    for msg in history:
        print(f"{msg['role']}: {msg['content']}")
    
    # 获取统计信息
    stats = manager.get_session_statistics()
    print(f"Statistics: {stats}")
    
    # 清理测试数据
    manager.delete_session(session_id)
    print("Test completed successfully!") 