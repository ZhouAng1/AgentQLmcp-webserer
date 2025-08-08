#!/usr/bin/env python3
"""
AgentQL MCP Integration for TinyWebServer AI Chat
Enables AI to get structured data from unstructured web content
Based on official AgentQL MCP server: https://github.com/tinyfish-io/agentql-mcp.git
"""

import requests
import json
import logging
from typing import Dict, Any, Optional
import yaml
import os
import subprocess
import sys

class AgentQLMCPClient:
    """AgentQL MCP Client using official MCP server"""
    
    def __init__(self, config_path: str = "config/ai_chat_config.yaml"):
        self.config = self._load_config(config_path)
        self.api_key = os.getenv('AGENTQL_API_KEY')
        
        if not self.api_key:
            logging.warning("AGENTQL_API_KEY not found in environment variables")
        
        # Check if agentql-mcp is available
        self.mcp_available = self._check_mcp_availability()
        
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            return {}
    
    def _check_mcp_availability(self) -> bool:
        """Check if agentql-mcp is available via npm"""
        try:
            result = subprocess.run(
                ['npx', 'agentql-mcp', '--version'],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0
        except Exception as e:
            logging.warning(f"AgentQL MCP not available: {str(e)}")
            return False
    
    def extract_web_data(self, url: str, prompt: str) -> Dict[str, Any]:
        """
        Extract structured data from web content using AgentQL MCP
        
        Args:
            url: Target webpage URL
            prompt: Description of data to extract
            
        Returns:
            Structured data extracted from the webpage
        """
        if not self.mcp_available:
            return {'error': 'AgentQL MCP server not available'}
        
        if not self.api_key:
            return {'error': 'AGENTQL_API_KEY not configured'}
        
        try:
            # Use npx to run agentql-mcp
            env = os.environ.copy()
            env['AGENTQL_API_KEY'] = self.api_key
            
            # Create MCP request
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
            
            # Run agentql-mcp via npx
            process = subprocess.Popen(
                ['npx', '-y', 'agentql-mcp'],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env,
                text=True
            )
            
            # Send request
            stdout, stderr = process.communicate(
                input=json.dumps(mcp_request) + '\n',
                timeout=60
            )
            
            if process.returncode != 0:
                logging.error(f"AgentQL MCP error: {stderr}")
                return {'error': f'MCP server error: {stderr}'}
            
            # Parse response
            try:
                response = json.loads(stdout.strip())
                if 'result' in response:
                    return response['result']
                elif 'error' in response:
                    return {'error': response['error']}
                else:
                    return {'error': 'Unexpected response format'}
            except json.JSONDecodeError:
                return {'error': 'Invalid JSON response from MCP server'}
                
        except subprocess.TimeoutExpired:
            process.kill()
            return {'error': 'MCP server timeout'}
        except Exception as e:
            logging.error(f"AgentQL MCP integration error: {str(e)}")
            return {'error': f'Integration error: {str(e)}'}
    
    def get_real_time_info(self, topic: str) -> Dict[str, Any]:
        """
        Get real-time information about a topic
        
        Args:
            topic: Topic to search for real-time information
            
        Returns:
            Real-time information about the topic
        """
        try:
            # Create a search prompt for the topic
            search_prompt = f"""
            Extract the following information about {topic}:
            1. Current status or latest news
            2. Key facts and figures
            3. Recent updates or changes
            4. Relevant statistics or data
            
            Format the response as structured data with clear sections.
            """
            
            # Use a reliable news or information source
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
                prompt = search_prompt
            
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
    """Enhanced AI Chat with AgentQL MCP integration"""
    
    def __init__(self):
        self.agentql_client = AgentQLMCPClient()
    
    def enhance_response_with_web_data(self, user_message: str, ai_response: str) -> str:
        """
        Enhance AI response with real-time web data using AgentQL MCP
        
        Args:
            user_message: Original user message
            ai_response: Initial AI response
            
        Returns:
            Enhanced response with web data
        """
        try:
            # Extract potential topics for real-time information
            topics = self._extract_topics(user_message)
            
            if not topics:
                return ai_response
            
            # Get real-time information for each topic
            web_data = {}
            for topic in topics[:2]:  # Limit to 2 topics to avoid rate limits
                real_time_info = self.agentql_client.get_real_time_info(topic)
                if 'error' not in real_time_info:
                    web_data[topic] = real_time_info
            
            if not web_data:
                return ai_response
            
            # Enhance the response with web data
            enhanced_response = self._combine_response_with_web_data(ai_response, web_data)
            return enhanced_response
            
        except Exception as e:
            logging.error(f"Response enhancement error: {str(e)}")
            return ai_response
    
    def _extract_topics(self, message: str) -> list:
        """Extract potential topics for real-time information"""
        # Simple topic extraction - can be enhanced with NLP
        topics = []
        
        # Common real-time topics
        real_time_keywords = [
            'weather', 'stock', 'price', 'news', 'crypto', 'bitcoin',
            'weather', 'temperature', 'forecast', 'market', 'trading',
            'latest', 'recent', 'current', 'today', 'now', '实时',
            '天气', '股票', '价格', '新闻', '加密货币', '比特币',
            '最新', '当前', '今天', '现在'
        ]
        
        message_lower = message.lower()
        for keyword in real_time_keywords:
            if keyword in message_lower:
                # Extract the topic around the keyword
                words = message.split()
                for i, word in enumerate(words):
                    if keyword in word.lower():
                        # Get surrounding words as topic
                        start = max(0, i-2)
                        end = min(len(words), i+3)
                        topic = ' '.join(words[start:end])
                        topics.append(topic)
                        break
        
        return list(set(topics))  # Remove duplicates
    
    def _combine_response_with_web_data(self, ai_response: str, web_data: Dict[str, Any]) -> str:
        """Combine AI response with web data"""
        enhanced_response = ai_response
        
        if web_data:
            enhanced_response += "\n\n**📊 实时信息补充 (AgentQL MCP):**\n"
            
            for topic, data in web_data.items():
                if 'extracted_data' in data and 'error' not in data['extracted_data']:
                    extracted = data['extracted_data']
                    if isinstance(extracted, dict) and 'content' in extracted:
                        enhanced_response += f"\n**{topic}:**\n{extracted['content']}\n"
                    elif isinstance(extracted, str):
                        enhanced_response += f"\n**{topic}:**\n{extracted}\n"
                    elif isinstance(extracted, dict):
                        # Handle structured data
                        for key, value in extracted.items():
                            enhanced_response += f"\n**{key}:** {value}\n"
            
            enhanced_response += f"\n*信息来源: AgentQL MCP 实时数据提取*"
        
        return enhanced_response

# Example usage
if __name__ == "__main__":
    # Test the AgentQL MCP integration
    enhanced_chat = EnhancedAIChat()
    
    # Test with a real-time query
    test_message = "What's the current weather in Beijing?"
    test_response = "Based on general knowledge, Beijing has a temperate climate with four distinct seasons."
    
    enhanced = enhanced_chat.enhance_response_with_web_data(test_message, test_response)
    print("Enhanced Response:")
    print(enhanced) 