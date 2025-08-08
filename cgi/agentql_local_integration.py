#!/usr/bin/env python3
"""
本地AgentQL MCP集成
使用本地AgentQL MCP仓库，无需npm安装
"""

import requests
import json
import logging
import subprocess
import os
import sys
from typing import Dict, Any, Optional
import yaml

class LocalAgentQLMCPClient:
    """使用本地AgentQL MCP仓库的客户端"""
    
    def __init__(self, config_path: str = "config/ai_chat_config.yaml"):
        self.config = self._load_config(config_path)
        self.api_key = os.getenv('AGENTQL_API_KEY')
        # 更新路径：agentql-mcp在工作区根目录，与TinyWebServer-master并列
        self.local_mcp_path = os.path.join(os.path.dirname(os.getcwd()), 'agentql-mcp')
        
        if not self.api_key:
            logging.warning("AGENTQL_API_KEY not found in environment variables")
        
        # 检查本地MCP仓库
        self.mcp_available = self._check_local_mcp()
        
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            return {}
    
    def _check_local_mcp(self) -> bool:
        """检查本地MCP仓库是否可用"""
        try:
            # 检查目录是否存在
            if not os.path.exists(self.local_mcp_path):
                logging.warning(f"Local MCP path not found: {self.local_mcp_path}")
                return False
            
            # 检查package.json是否存在
            package_json = os.path.join(self.local_mcp_path, 'package.json')
            if not os.path.exists(package_json):
                logging.warning("package.json not found in local MCP")
                return False
            
            # 检查是否已构建
            dist_path = os.path.join(self.local_mcp_path, 'dist', 'index.js')
            if not os.path.exists(dist_path):
                logging.info("Building local MCP...")
                return self._build_local_mcp()
            
            return True
            
        except Exception as e:
            logging.error(f"Local MCP check failed: {str(e)}")
            return False
    
    def _build_local_mcp(self) -> bool:
        """构建本地MCP"""
        try:
            # 安装依赖
            install_result = subprocess.run(
                ['npm', 'install'],
                cwd=self.local_mcp_path,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if install_result.returncode != 0:
                logging.error(f"npm install failed: {install_result.stderr}")
                return False
            
            # 构建项目
            build_result = subprocess.run(
                ['npm', 'run', 'build'],
                cwd=self.local_mcp_path,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if build_result.returncode != 0:
                logging.error(f"npm build failed: {build_result.stderr}")
                return False
            
            logging.info("Local MCP built successfully")
            return True
            
        except subprocess.TimeoutExpired:
            logging.error("Local MCP build timeout")
            return False
        except Exception as e:
            logging.error(f"Local MCP build error: {str(e)}")
            return False
    
    def extract_web_data(self, url: str, prompt: str) -> Dict[str, Any]:
        """
        使用本地MCP提取网页数据
        
        Args:
            url: 目标网页URL
            prompt: 数据提取描述
            
        Returns:
            提取的结构化数据
        """
        if not self.mcp_available:
            return {'error': 'Local MCP not available'}
        
        if not self.api_key:
            return {'error': 'AGENTQL_API_KEY not configured'}
        
        try:
            # 创建MCP请求
            mcp_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {
                    "name": "extract-web-data",
                    "arguments": {
                        "url": url,
                        "prompt": prompt
                    }
                }
            }
            
            # 设置环境变量
            env = os.environ.copy()
            env['AGENTQL_API_KEY'] = self.api_key
            
            # 运行本地MCP
            mcp_executable = os.path.join(self.local_mcp_path, 'dist', 'index.js')
            process = subprocess.Popen(
                ['node', mcp_executable],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env,
                text=True
            )
            
            # 发送请求
            stdout, stderr = process.communicate(
                input=json.dumps(mcp_request) + '\n',
                timeout=60
            )
            
            if process.returncode != 0:
                logging.error(f"Local MCP error: {stderr}")
                return {'error': f'Local MCP error: {stderr}'}
            
            # 解析响应
            try:
                response = json.loads(stdout.strip())
                if 'result' in response:
                    return response['result']
                elif 'error' in response:
                    return {'error': response['error']}
                else:
                    return {'error': 'Unexpected response format'}
            except json.JSONDecodeError:
                return {'error': 'Invalid JSON response from local MCP'}
                
        except subprocess.TimeoutExpired:
            process.kill()
            return {'error': 'Local MCP timeout'}
        except Exception as e:
            logging.error(f"Local MCP integration error: {str(e)}")
            return {'error': f'Integration error: {str(e)}'}
    
    def get_real_time_info(self, topic: str) -> Dict[str, Any]:
        """
        获取实时信息
        
        Args:
            topic: 主题
            
        Returns:
            实时信息
        """
        try:
            # 根据主题选择合适的数据源
            if 'weather' in topic.lower() or '天气' in topic:
                url = "https://www.weather.com"
                prompt = f"Extract current weather information for {topic}"
            elif 'stock' in topic.lower() or '股票' in topic:
                url = "https://finance.yahoo.com"
                prompt = f"Extract current stock information for {topic}"
            elif 'crypto' in topic.lower() or 'bitcoin' in topic.lower():
                url = "https://coinmarketcap.com"
                prompt = f"Extract current cryptocurrency information for {topic}"
            else:
                url = "https://www.google.com"
                prompt = f"Extract current information about {topic}"
            
            extracted_data = self.extract_web_data(url, prompt)
            
            return {
                'topic': topic,
                'source_url': url,
                'extracted_data': extracted_data
            }
            
        except Exception as e:
            logging.error(f"Real-time info error: {str(e)}")
            return {'error': f'Real-time info error: {str(e)}'}

class EnhancedAIChat:
    """增强AI聊天，支持本地AgentQL MCP"""
    
    def __init__(self, use_local_mcp: bool = True):
        if use_local_mcp:
            self.agentql_client = LocalAgentQLMCPClient()
        else:
            # 回退到简化版本
            from agentql_simple_integration import MockAgentQLClient
            self.agentql_client = MockAgentQLClient()
    
    def enhance_response_with_web_data(self, user_message: str, ai_response: str) -> str:
        """
        使用实时数据增强AI回复
        
        Args:
            user_message: 用户消息
            ai_response: AI回复
            
        Returns:
            增强后的回复
        """
        try:
            # 提取潜在主题
            topics = self._extract_topics(user_message)
            
            if not topics:
                return ai_response
            
            # 获取实时信息
            web_data = {}
            for topic in topics[:2]:  # 限制为2个主题
                real_time_info = self.agentql_client.get_real_time_info(topic)
                if 'error' not in real_time_info:
                    web_data[topic] = real_time_info
            
            if not web_data:
                return ai_response
            
            # 结合实时数据
            enhanced_response = self._combine_response_with_web_data(ai_response, web_data)
            return enhanced_response
            
        except Exception as e:
            logging.error(f"Response enhancement error: {str(e)}")
            return ai_response
    
    def _extract_topics(self, message: str) -> list:
        """提取潜在主题"""
        topics = []
        
        # 实时关键词
        real_time_keywords = [
            'weather', 'stock', 'price', 'news', 'crypto', 'bitcoin',
            'temperature', 'forecast', 'market', 'trading',
            'latest', 'recent', 'current', 'today', 'now', '实时',
            '天气', '股票', '价格', '新闻', '加密货币', '比特币',
            '最新', '当前', '今天', '现在'
        ]
        
        message_lower = message.lower()
        for keyword in real_time_keywords:
            if keyword in message_lower:
                # 提取关键词周围的词作为主题
                words = message.split()
                for i, word in enumerate(words):
                    if keyword in word.lower():
                        start = max(0, i-2)
                        end = min(len(words), i+3)
                        topic = ' '.join(words[start:end])
                        topics.append(topic)
                        break
        
        return list(set(topics))  # 去重
    
    def _combine_response_with_web_data(self, ai_response: str, web_data: Dict[str, Any]) -> str:
        """结合AI回复和实时数据"""
        enhanced_response = ai_response
        
        if web_data:
            enhanced_response += "\n\n**📊 实时信息补充 (本地AgentQL MCP):**\n"
            
            for topic, data in web_data.items():
                if 'extracted_data' in data and 'error' not in data['extracted_data']:
                    extracted = data['extracted_data']
                    if isinstance(extracted, dict) and 'content' in extracted:
                        enhanced_response += f"\n**{topic}:**\n{extracted['content']}\n"
                    elif isinstance(extracted, str):
                        enhanced_response += f"\n**{topic}:**\n{extracted}\n"
                    elif isinstance(extracted, dict):
                        # 处理结构化数据
                        for key, value in extracted.items():
                            if key != 'content':
                                enhanced_response += f"\n**{key}:** {value}\n"
            
            enhanced_response += f"\n*信息来源: 本地AgentQL MCP 实时数据提取*"
        
        return enhanced_response

# 测试代码
if __name__ == "__main__":
    # 测试本地MCP集成
    enhanced_chat = EnhancedAIChat(use_local_mcp=True)
    
    test_cases = [
        "北京今天天气怎么样？",
        "苹果股票现在多少钱？",
        "比特币价格如何？",
        "有什么最新科技新闻？"
    ]
    
    for test_message in test_cases:
        print(f"\n测试: {test_message}")
        test_response = "基于一般知识，我无法提供实时信息。"
        enhanced = enhanced_chat.enhance_response_with_web_data(test_message, test_response)
        print(f"增强回复: {enhanced}") 