#!/bin/bash

echo "🚀 启动 AI 聊天服务器"
echo "===================="

# 设置API密钥（请替换为你的DeepSeek API密钥）
export DEEPSEEK_API_KEY="your_deepseek_api_key_here"

# 安装Python依赖
echo "🐍 安装Python依赖..."
pip3 install -r cgi/requirements.txt 2>/dev/null || {
    echo "⚠️  Python依赖安装失败，尝试使用pip..."
    pip install -r cgi/requirements.txt 2>/dev/null || {
        echo "⚠️  Python依赖安装失败，继续启动..."
    }
}

# 设置权限
chmod +x cgi/*.py

# 初始化数据库
echo "🗄️  初始化数据库..."
mysql -u root -proot < init_db.sql 2>/dev/null || {
    echo "⚠️  数据库初始化失败，继续启动..."
}

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