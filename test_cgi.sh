#!/bin/bash

echo "🧪 测试CGI功能"
echo "=============="

# 设置环境变量
export DEEPSEEK_API_KEY="sk-7d3a5f1e93184ef8a00ab4e8c6fa6677"
export CONTENT_LENGTH="35"
export REQUEST_METHOD="POST"

echo "🔑 API Key: ${DEEPSEEK_API_KEY:0:10}..."

# 测试CGI脚本
echo "📝 测试消息: hello"
echo '{"message":"hello","model":"deepseek"}' | python3 cgi/ai_chat.py

echo ""
echo "✅ 测试完成" 