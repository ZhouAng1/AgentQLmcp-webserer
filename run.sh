#!/bin/bash

echo "🚀 启动 AI 聊天服务器"
echo "===================="

# 设置API密钥
export DEEPSEEK_API_KEY="sk-7d3a5f1e93184ef8a00ab4e8c6fa6677"

# 设置权限
chmod +x cgi/*.py

# 编译
make clean && make

# 启动服务器
echo "✅ 服务器启动中..."
echo "🌐 访问: http://localhost:9006/chat.html"
echo "按 Ctrl+C 停止"
echo "===================="

./server 