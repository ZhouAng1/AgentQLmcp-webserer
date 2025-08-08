#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import requests
import os
import sys
import sqlite3
import uuid
import time
import yaml
import logging
from typing import Dict, List, Optional

# Import AgentQL integration
try:
    from agentql_final_integration import EnhancedAIChat
    AGENTQL_AVAILABLE = True
except ImportError:
    AGENTQL_AVAILABLE = False
    logging.warning("AgentQL integration not available")

class MCPClient:
    def __init__(self):
        self.models = {
            "gpt-3.5-turbo": {
                "api_key": os.getenv('OPENAI_API_KEY'),
                "base_url": "https://api.openai.com/v1/chat/completions"
            },
            "claude": {
                "api_key": os.getenv('ANTHROPIC_API_KEY'),
                "base_url": "https://api.anthropic.com/v1/messages"
            },
            "deepseek": {
                "api_key": os.getenv('DEEPSEEK_API_KEY'),
                "base_url": "https://api.deepseek.com/v1/chat/completions"
            }
        }
        
        # Initialize AgentQL integration if available
        self.agentql_enabled = False
        if AGENTQL_AVAILABLE:
            try:
                self.enhanced_chat = EnhancedAIChat()
                self.agentql_enabled = True
            except Exception as e:
                logging.error(f"Failed to initialize AgentQL: {str(e)}")
        
    def chat_with_model(self, message: str, model_name: str = "gpt-3.5-turbo", 
                       conversation_history: List[Dict] = []) -> Dict:
        if model_name not in self.models:
            return {"success": False, "error": f"Model {model_name} not supported"}
            
        model_config = self.models[model_name]
        
        # Get base AI response
        if model_name == "gpt-3.5-turbo":
            result = self._call_openai(message, conversation_history, model_config)
        elif model_name == "claude":
            result = self._call_anthropic(message, conversation_history, model_config)
        elif model_name == "deepseek":
            result = self._call_deepseek(message, conversation_history, model_config)
        
        # Enhance response with AgentQL if enabled and applicable
        if result["success"] and self.agentql_enabled and self._should_enhance_with_agentql(message):
            try:
                enhanced_response = self.enhanced_chat.enhance_response_with_web_data(
                    message, result["response"]
                )
                result["response"] = enhanced_response
                result["agentql_enhanced"] = True
            except Exception as e:
                logging.error(f"AgentQL enhancement failed: {str(e)}")
                result["agentql_enhanced"] = False
        
        return result
    
    def _should_enhance_with_agentql(self, message: str) -> bool:
        """Determine if message should be enhanced with AgentQL"""
        if not self.agentql_enabled:
            return False
        
        # Check if message contains real-time keywords
        real_time_keywords = [
            'weather', 'stock', 'price', 'news', 'crypto', 'bitcoin',
            'weather', 'temperature', 'forecast', 'market', 'trading',
            'latest', 'recent', 'current', 'today', 'now', '实时',
            '天气', '股票', '价格', '新闻', '加密货币', '比特币',
            '最新', '当前', '今天', '现在'
        ]
        
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in real_time_keywords)
            
    def _call_openai(self, message: str, conversation_history: List[Dict], config: Dict) -> Dict:
        if not config['api_key']:
            return {"success": False, "error": "OpenAI API key not configured"}
            
        headers = {
            "Authorization": f"Bearer {config['api_key']}",
            "Content-Type": "application/json"
        }
        
        messages = conversation_history + [{"role": "user", "content": message}]
        
        data = {
            "model": "gpt-3.5-turbo",
            "messages": messages,
            "max_tokens": 1000,
            "temperature": 0.7
        }
        
        try:
            response = requests.post(config['base_url'], headers=headers, json=data, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            return {
                "success": True,
                "response": result['choices'][0]['message']['content'],
                "usage": result.get('usage', {}),
                "model": "gpt-3.5-turbo"
            }
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": f"OpenAI API error: {str(e)}"}
        except Exception as e:
            return {"success": False, "error": f"Unexpected error: {str(e)}"}
    
    def _call_anthropic(self, message: str, conversation_history: List[Dict], config: Dict) -> Dict:
        if not config['api_key']:
            return {"success": False, "error": "Anthropic API key not configured"}
            
        headers = {
            "x-api-key": config['api_key'],
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }
        
        # 构建Claude格式的消息
        messages = []
        for msg in conversation_history:
            messages.append({"role": msg["role"], "content": msg["content"]})
        messages.append({"role": "user", "content": message})
        
        data = {
            "model": "claude-3-sonnet-20240229",
            "max_tokens": 1000,
            "messages": messages
        }
        
        try:
            response = requests.post(config['base_url'], headers=headers, json=data, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            return {
                "success": True,
                "response": result['content'][0]['text'],
                "usage": result.get('usage', {}),
                "model": "claude"
            }
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": f"Anthropic API error: {str(e)}"}
        except Exception as e:
            return {"success": False, "error": f"Unexpected error: {str(e)}"}
    
    def _call_deepseek(self, message: str, conversation_history: List[Dict], config: Dict) -> Dict:
        if not config['api_key']:
            return {"success": False, "error": "DeepSeek API key not configured"}
            
        headers = {
            "Authorization": f"Bearer {config['api_key']}",
            "Content-Type": "application/json"
        }
        
        messages = conversation_history + [{"role": "user", "content": message}]
        
        data = {
            "model": "deepseek-chat",
            "messages": messages,
            "max_tokens": 1000,
            "temperature": 0.7
        }
        
        try:
            response = requests.post(config['base_url'], headers=headers, json=data, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            return {
                "success": True,
                "response": result['choices'][0]['message']['content'],
                "usage": result.get('usage', {}),
                "model": "deepseek"
            }
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": f"DeepSeek API error: {str(e)}"}
        except Exception as e:
            return {"success": False, "error": f"Unexpected error: {str(e)}"}

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
    
    def cleanup_old_sessions(self, days: int = 7):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "DELETE FROM sessions WHERE last_activity < datetime('now', '-{} days')".format(days)
        )
        
        conn.commit()
        conn.close()

# CGI处理
def main():
    print("Content-Type: application/json")
    print()
    
    try:
        # 读取POST数据
        content_length = int(os.environ.get('CONTENT_LENGTH', 0))
        if content_length > 0:
            post_data = sys.stdin.read(content_length)
            request_data = json.loads(post_data)
        else:
            request_data = {}
        
        # 获取用户消息和模型选择
        user_message = request_data.get('message', '')
        model_name = request_data.get('model', 'gpt-3.5-turbo')
        session_id = request_data.get('session_id', None)
        
        if not user_message:
            raise ValueError("No message provided")
        
        # 创建MCP客户端
        mcp_client = MCPClient()
        
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
        result = mcp_client.chat_with_model(user_message, model_name, conversation_history)
        
        if result["success"]:
            # 添加AI回复到历史
            session_manager.add_message(session_id, "assistant", result["response"])
        
        # 返回结果
        response = {
            "success": result["success"],
            "response": result.get("response", "Sorry, I couldn't process your request."),
            "usage": result.get("usage", {}),
            "model": result.get("model", model_name),
            "session_id": session_id,
            "agentql_enabled": mcp_client.agentql_enabled,
            "agentql_enhanced": result.get("agentql_enhanced", False)
        }
        
        print(json.dumps(response))
        
    except json.JSONDecodeError as e:
        error_response = {
            "success": False,
            "error": f"Invalid JSON: {str(e)}"
        }
        print(json.dumps(error_response))
    except ValueError as e:
        error_response = {
            "success": False,
            "error": str(e)
        }
        print(json.dumps(error_response))
    except Exception as e:
        error_response = {
            "success": False,
            "error": f"Unexpected error: {str(e)}"
        }
        print(json.dumps(error_response))

if __name__ == "__main__":
    main() 