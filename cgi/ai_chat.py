#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import requests
import os
import sys
import sqlite3
import uuid
import time
import logging
from typing import Dict, List, Optional

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DeepSeekClient:
    def __init__(self):
        self.api_key = os.getenv('DEEPSEEK_API_KEY')
        self.base_url = "https://api.deepseek.com/v1/chat/completions"
        
        logger.info(f"DeepSeek API Key: {'SET' if self.api_key else 'NOT_SET'}")
        
    def chat(self, message: str, conversation_history: List[Dict] = []) -> Dict:
        if not self.api_key:
            return {"success": False, "error": "DeepSeek API key not configured"}
            
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        messages = conversation_history + [{"role": "user", "content": message}]
        
        data = {
            "model": "deepseek-chat",
            "messages": messages,
            "max_tokens": 1000,
            "temperature": 0.7
        }
        
        logger.info(f"Calling DeepSeek API with message: {message[:50]}...")
        
        try:
            response = requests.post(self.base_url, headers=headers, json=data, timeout=30)
            logger.info(f"DeepSeek response status: {response.status_code}")
            
            if response.status_code != 200:
                logger.error(f"DeepSeek API error: {response.status_code} - {response.text}")
                return {"success": False, "error": f"DeepSeek API error: {response.status_code}"}
            
            result = response.json()
            return {
                "success": True,
                "response": result['choices'][0]['message']['content'],
                "usage": result.get('usage', {}),
                "model": "deepseek"
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"DeepSeek request error: {str(e)}")
            return {"success": False, "error": f"DeepSeek API error: {str(e)}"}
        except Exception as e:
            logger.error(f"DeepSeek unexpected error: {str(e)}")
            return {"success": False, "error": f"Unexpected error: {str(e)}"}

class SessionManager:
    def __init__(self, db_path="chat_sessions.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
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
        
        conn.commit()
        conn.close()
    
    def create_session(self) -> str:
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

# CGI处理
def main():
    logger.info("=== CGI Script Started ===")
    logger.info(f"CONTENT_LENGTH: {os.environ.get('CONTENT_LENGTH', 'NOT_SET')}")
    logger.info(f"REQUEST_METHOD: {os.environ.get('REQUEST_METHOD', 'NOT_SET')}")
    
    print("Content-Type: application/json")
    print()
    
    try:
        # 读取POST数据
        content_length = int(os.environ.get('CONTENT_LENGTH', 0))
        logger.info(f"Content length: {content_length}")
        
        if content_length > 0:
            post_data = sys.stdin.read(content_length)
            logger.info(f"Post data: {post_data[:100]}...")
            request_data = json.loads(post_data)
        else:
            request_data = {}
        
        # 获取用户消息和会话ID
        user_message = request_data.get('message', '')
        session_id = request_data.get('session_id', None)
        
        logger.info(f"User message: {user_message}")
        logger.info(f"Session ID: {session_id}")
        
        if not user_message:
            raise ValueError("No message provided")
        
        # 创建DeepSeek客户端
        deepseek_client = DeepSeekClient()
        
        # 创建会话管理器
        session_manager = SessionManager()
        
        # 如果没有会话ID，创建一个新的
        if not session_id:
            session_id = session_manager.create_session()
        
        # 获取对话历史
        conversation_history = session_manager.get_conversation_history(session_id)
        
        # 添加用户消息到历史
        session_manager.add_message(session_id, "user", user_message)
        
        # 调用AI
        result = deepseek_client.chat(user_message, conversation_history)
        
        if result["success"]:
            # 添加AI回复到历史
            session_manager.add_message(session_id, "assistant", result["response"])
        
        # 返回结果
        response = {
            "success": result["success"],
            "response": result.get("response", "Sorry, I couldn't process your request."),
            "usage": result.get("usage", {}),
            "model": result.get("model", "deepseek"),
            "session_id": session_id
        }
        
        logger.info("=== CGI Script Completed Successfully ===")
        print(json.dumps(response))
        
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {str(e)}")
        error_response = {
            "success": False,
            "error": f"Invalid JSON: {str(e)}"
        }
        print(json.dumps(error_response))
    except ValueError as e:
        logger.error(f"Value error: {str(e)}")
        error_response = {
            "success": False,
            "error": str(e)
        }
        print(json.dumps(error_response))
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        error_response = {
            "success": False,
            "error": f"Unexpected error: {str(e)}"
        }
        print(json.dumps(error_response))

if __name__ == "__main__":
    main() 