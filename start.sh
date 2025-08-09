#!/bin/bash

echo "🚀 启动 AgentQL WebServer AI 聊天系统"
echo "=================================="

# 检查是否在项目根目录
if [ ! -f "main.cpp" ]; then
    echo "❌ 请在项目根目录运行此脚本"
    exit 1
fi

# 设置环境变量
export DEEPSEEK_API_KEY="sk-7d3a5f1e93184ef8a00ab4e8c6fa6677"

echo "✅ 环境变量已设置"
echo "🔑 DeepSeek API Key: ${DEEPSEEK_API_KEY:0:10}..."

# 检查并杀死已存在的服务器进程
echo "🔍 检查现有进程..."
pkill -f server 2>/dev/null || true
sleep 2

# 检查端口占用
if netstat -tlnp 2>/dev/null | grep -q ":9006 "; then
    echo "⚠️  端口9006被占用，正在释放..."
    sudo fuser -k 9006/tcp 2>/dev/null || true
    sleep 2
fi

# 设置CGI脚本权限
echo "🔐 设置脚本权限..."
chmod +x cgi/*.py

# 编译服务器
echo "🔨 编译服务器..."
make clean
make

if [ ! -f "server" ]; then
    echo "❌ 编译失败！"
    exit 1
fi

echo "✅ 编译成功！"

# 启动服务器
echo "🚀 启动服务器..."
echo "📡 服务器将在端口 9006 上运行"
echo "🌐 访问地址: http://localhost:9006/chat.html"
echo ""
echo "按 Ctrl+C 停止服务器"
echo "=================================="

# 启动服务器
./server 