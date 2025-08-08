#!/usr/bin/env python3
"""
最终AgentQL集成方案
支持多种模式：模拟数据、直接API、本地MCP
"""

import requests
import json
import logging
import subprocess
import os
import sys
from typing import Dict, Any, Optional
import yaml

class AgentQLClient:
    """统一的AgentQL客户端，支持多种模式"""
    
    def __init__(self, mode: str = "mock", config_path: str = "config/ai_chat_config.yaml"):
        self.config = self._load_config(config_path)
        self.mode = mode
        self.api_key = os.getenv('AGENTQL_API_KEY')
        
        if mode == "local_mcp":
            self.local_mcp_path = os.path.join(os.path.dirname(os.getcwd()), 'agentql-mcp')
            self.mcp_available = self._check_local_mcp()
        elif mode == "direct_api":
            self.api_endpoint = 'https://api.agentql.com/v1/query-data'
        
        if not self.api_key and mode != "mock":
            logging.warning("AGENTQL_API_KEY not found in environment variables")
        
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
            if not os.path.exists(self.local_mcp_path):
                logging.warning(f"Local MCP path not found: {self.local_mcp_path}")
                return False
            
            dist_path = os.path.join(self.local_mcp_path, 'dist', 'index.js')
            if not os.path.exists(dist_path):
                logging.warning("Local MCP not built, falling back to direct API")
                return False
            
            return True
            
        except Exception as e:
            logging.error(f"Local MCP check failed: {str(e)}")
            return False
    
    def extract_web_data(self, url: str, prompt: str) -> Dict[str, Any]:
        """
        提取网页数据，根据模式选择不同实现
        
        Args:
            url: 目标网页URL
            prompt: 数据提取描述
            
        Returns:
            提取的结构化数据
        """
        if self.mode == "mock":
            return self._extract_mock_data(url, prompt)
        elif self.mode == "local_mcp" and self.mcp_available:
            return self._extract_local_mcp(url, prompt)
        elif self.mode == "direct_api" or self.mode == "local_mcp":
            return self._extract_direct_api(url, prompt)
        else:
            return {'error': f'Mode {self.mode} not available'}
    
    def _extract_mock_data(self, url: str, prompt: str) -> Dict[str, Any]:
        """模拟数据提取"""
        # 根据URL和prompt返回模拟数据
        if 'weather' in url.lower() or '天气' in prompt:
            return {
                'temperature': '15-22°C',
                'condition': '多云',
                'humidity': '65%',
                'wind_speed': '3级'
            }
        elif 'stock' in url.lower() or '股票' in prompt:
            return {
                'price': '$175.43',
                'change': '+2.1%',
                'volume': '1.2B',
                'market_cap': '$2.8T'
            }
        elif 'crypto' in url.lower() or 'bitcoin' in prompt.lower():
            return {
                'price': '$43,250',
                'change_24h': '+3.2%',
                'market_cap': '$850B',
                'volume_24h': '$25B'
            }
        else:
            return {
                'title': '模拟数据',
                'content': '这是模拟的实时数据',
                'timestamp': '2024-01-15T10:30:00Z'
            }
    
    def _extract_local_mcp(self, url: str, prompt: str) -> Dict[str, Any]:
        """使用本地MCP提取数据"""
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
    
    def _extract_direct_api(self, url: str, prompt: str) -> Dict[str, Any]:
        """直接调用AgentQL API"""
        if not self.api_key:
            return {'error': 'AGENTQL_API_KEY not configured'}
        
        try:
            headers = {
                'X-API-Key': self.api_key,
                'X-TF-Request-Origin': 'mcp-server',
                'Content-Type': 'application/json',
            }
            
            payload = {
                'url': url,
                'prompt': prompt,
                'params': {
                    'wait_for': 0,
                    'is_scroll_to_bottom_enabled': False,
                    'mode': 'fast',
                    'is_screenshot_enabled': False,
                },
            }
            
            response = requests.post(
                self.api_endpoint,
                headers=headers,
                json=payload,
                timeout=60
            )
            
            if not response.ok:
                error_text = response.text
                logging.error(f"AgentQL API error: {response.status_code} - {error_text}")
                return {'error': f'API error: {response.status_code} - {error_text}'}
            
            result = response.json()
            
            # 返回data字段，与MCP服务器保持一致
            if 'data' in result:
                return result['data']
            else:
                return result
                
        except requests.exceptions.RequestException as e:
            logging.error(f"AgentQL API request error: {str(e)}")
            return {'error': f'Request error: {str(e)}'}
        except Exception as e:
            logging.error(f"AgentQL API integration error: {str(e)}")
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
                'extracted_data': extracted_data,
                'mode': self.mode
            }
            
        except Exception as e:
            logging.error(f"Real-time info error: {str(e)}")
            return {'error': f'Real-time info error: {str(e)}'}

class EnhancedAIChat:
    """增强AI聊天，支持多种AgentQL模式"""
    
    def __init__(self, mode: str = "mock"):
        """
        初始化增强AI聊天
        
        Args:
            mode: 模式选择
                - "mock": 使用模拟数据（默认）
                - "direct_api": 使用直接API
                - "local_mcp": 使用本地MCP
        """
        self.agentql_client = AgentQLClient(mode=mode)
        self.mode = mode
    
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
            mode_display = {
                "mock": "模拟数据",
                "direct_api": "AgentQL API",
                "local_mcp": "本地MCP"
            }.get(self.mode, self.mode)
            
            enhanced_response += f"\n\n**📊 实时信息补充 ({mode_display}):**\n"
            
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
            
            enhanced_response += f"\n*信息来源: {mode_display} 实时数据提取*"
        
        return enhanced_response

# 测试代码
if __name__ == "__main__":
    # 测试不同模式
    modes = ["mock", "direct_api", "local_mcp"]
    
    for mode in modes:
        print(f"\n=== 测试模式: {mode} ===")
        enhanced_chat = EnhancedAIChat(mode=mode)
        
        test_cases = [
            "北京今天天气怎么样？",
            "苹果股票现在多少钱？",
            "比特币价格如何？"
        ]
        
        for test_message in test_cases:
            print(f"\n测试: {test_message}")
            test_response = "基于一般知识，我无法提供实时信息。"
            enhanced = enhanced_chat.enhance_response_with_web_data(test_message, test_response)
            print(f"增强回复: {enhanced}") 