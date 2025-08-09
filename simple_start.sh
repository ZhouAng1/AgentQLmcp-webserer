#!/bin/bash

echo "🚀 简化启动 AgentQL WebServer AI 聊天系统"
echo "=================================="

# 设置环境变量
export DEEPSEEK_API_KEY="sk-7d3a5f1e93184ef8a00ab4e8c6fa6677"

echo "✅ 环境变量已设置"

# 杀死已存在的服务器进程
echo "🔍 清理现有进程..."
pkill -f server 2>/dev/null || true
sleep 1

# 设置CGI脚本权限
echo "🔐 设置脚本权限..."
chmod +x cgi/*.py

# 编译服务器
echo "🔨 编译服务器..."
make clean
make

if [ ! -f "server" ]; then
    echo "❌ 编译失败！"
    echo "请检查错误信息"
    read -p "按回车键退出..."
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

# 启动服务器（保持终端不退出）
./server 