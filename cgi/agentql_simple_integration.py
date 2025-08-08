#!/usr/bin/env python3
"""
简化版AgentQL集成
使用HTTP API而不是MCP服务器，避免npm依赖
"""

import requests
import json
import logging
from typing import Dict, Any, Optional
import yaml
import os

class SimpleAgentQLClient:
    """简化版AgentQL客户端，使用HTTP API"""
    
    def __init__(self, config_path: str = "config/ai_chat_config.yaml"):
        self.config = self._load_config(config_path)
        self.api_key = os.getenv('AGENTQL_API_KEY')
        self.base_url = "https://api.agentql.com"  # 假设的API端点
        
        if not self.api_key:
            logging.warning("AGENTQL_API_KEY not found in environment variables")
        
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            return {}
    
    def extract_web_data(self, url: str, prompt: str) -> Dict[str, Any]:
        """
        从网页提取结构化数据
        
        Args:
            url: 目标网页URL
            prompt: 数据提取描述
            
        Returns:
            提取的结构化数据
        """
        if not self.api_key:
            return {'error': 'AGENTQL_API_KEY not configured'}
        
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'url': url,
                'prompt': prompt,
                'format': 'json'
            }
            
            response = requests.post(
                f"{self.base_url}/extract",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logging.error(f"AgentQL API request failed: {response.status_code}")
                return {'error': f'API request failed: {response.status_code}'}
                
        except requests.exceptions.RequestException as e:
            logging.error(f"AgentQL API error: {str(e)}")
            return {'error': f'API error: {str(e)}'}
        except Exception as e:
            logging.error(f"AgentQL integration error: {str(e)}")
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

class MockAgentQLClient:
    """模拟AgentQL客户端，用于演示"""
    
    def __init__(self):
        self.mock_data = {
            'weather': {
                '北京天气': '多云，温度15-22°C，湿度65%，风速3级',
                '上海天气': '晴天，温度18-25°C，湿度55%，风速2级',
                '深圳天气': '小雨，温度20-28°C，湿度75%，风速4级'
            },
            'stock': {
                '苹果股票': '当前价格$175.43，涨跌幅+2.1%，成交量1.2B',
                '特斯拉股票': '当前价格$245.67，涨跌幅-1.5%，成交量890M',
                '微软股票': '当前价格$398.12，涨跌幅+0.8%，成交量950M'
            },
            'crypto': {
                '比特币': '当前价格$43,250，24小时涨跌幅+3.2%，市值$850B',
                '以太坊': '当前价格$2,680，24小时涨跌幅+1.8%，市值$320B',
                '币安币': '当前价格$312，24小时涨跌幅-0.5%，市值$48B'
            },
            'news': {
                '科技新闻': 'OpenAI发布GPT-5预览版，特斯拉Q4财报超预期',
                '财经新闻': '美联储维持利率不变，美股三大指数上涨',
                '体育新闻': 'NBA季后赛即将开始，湖人队获得西部第八种子'
            }
        }
    
    def get_real_time_info(self, topic: str) -> Dict[str, Any]:
        """获取模拟实时信息"""
        topic_lower = topic.lower()
        
        for category, data in self.mock_data.items():
            for key, value in data.items():
                if any(word in topic_lower for word in key.lower().split()):
                    return {
                        'topic': topic,
                        'source_url': f'https://mock-{category}.com',
                        'extracted_data': {
                            'content': value,
                            'category': category,
                            'timestamp': '2024-01-15T10:30:00Z'
                        }
                    }
        
        return {'error': 'No relevant information found'}

class EnhancedAIChat:
    """增强AI聊天，支持实时数据"""
    
    def __init__(self, use_mock: bool = True):
        if use_mock:
            self.agentql_client = MockAgentQLClient()
        else:
            self.agentql_client = SimpleAgentQLClient()
    
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
            enhanced_response += "\n\n**📊 实时信息补充:**\n"
            
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
            
            enhanced_response += f"\n*信息来源: AgentQL 实时数据提取*"
        
        return enhanced_response

# 测试代码
if __name__ == "__main__":
    # 测试模拟客户端
    enhanced_chat = EnhancedAIChat(use_mock=True)
    
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