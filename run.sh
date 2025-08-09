#!/bin/bash

echo "🚀 启动 AI 聊天服务器"
echo "===================="

# 设置API密钥
export DEEPSEEK_API_KEY="sk-7d3a5f1e93184ef8a00ab4e8c6fa6677"

# 设置权限
chmod +x cgi/*.py

# 清理（忽略错误）
echo "🧹 清理旧文件..."
make clean 2>/dev/null || true

# 编译
echo "🔨 编译服务器..."
make

# 检查编译是否成功
if [ ! -f "server" ]; then
    echo "❌ 编译失败！请检查错误信息"
    echo "可能需要安装依赖："
    echo "sudo apt install -y mysql-server mysql-client g++ make"
    exit 1
fi

# 启动服务器
echo "✅ 服务器启动中..."
echo "🌐 访问: http://localhost:9006/chat.html"
echo "按 Ctrl+C 停止"
echo "===================="

./server 