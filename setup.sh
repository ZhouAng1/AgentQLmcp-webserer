#!/bin/bash

echo "🚀 AgentQL WebServer 一键安装脚本"
echo "=================================="

# 检查是否为root用户
if [ "$EUID" -eq 0 ]; then
    echo "❌ 请不要使用root用户运行此脚本"
    exit 1
fi

# 更新系统包
echo "📦 更新系统包..."
sudo apt update

# 安装基础编译工具
echo "🔧 安装编译工具..."
sudo apt install -y build-essential g++ make

# 安装Python相关
echo "🐍 安装Python环境..."
sudo apt install -y python3 python3-pip python3-venv python3-full

# 安装Python依赖包
echo "📚 安装Python依赖..."
sudo apt install -y python3-requests python3-yaml python3-sqlite3

# 安装MySQL（如果需要数据库功能）
echo "🗄️ 安装MySQL..."
sudo apt install -y mysql-server mysql-client libmysqlclient-dev

# 创建虚拟环境（备用方案）
echo "🔧 创建Python虚拟环境..."
python3 -m venv venv

# 激活虚拟环境并安装依赖
echo "📦 在虚拟环境中安装依赖..."
source venv/bin/activate
pip install requests pyyaml

# 设置CGI脚本权限
echo "🔐 设置脚本权限..."
chmod +x cgi/*.py

# 编译服务器
echo "🔨 编译Web服务器..."
make clean
make

# 检查编译结果
if [ -f "server" ]; then
    echo "✅ 服务器编译成功！"
else
    echo "❌ 服务器编译失败，请检查错误信息"
    exit 1
fi

# 创建配置文件（如果不存在）
if [ ! -f "config/ai_chat_config.yaml" ]; then
    echo "📝 创建配置文件..."
    mkdir -p config
    cat > config/ai_chat_config.yaml << EOF
# AI聊天配置
ai_models:
  gpt-3.5-turbo:
    enabled: true
    api_key_env: OPENAI_API_KEY
  claude:
    enabled: true
    api_key_env: ANTHROPIC_API_KEY
  deepseek:
    enabled: true
    api_key_env: DEEPSEEK_API_KEY

# AgentQL配置
agentql:
  mode: "mock"  # mock, direct_api, local_mcp
  enabled: true
  api_key_env: AGENTQL_API_KEY

# 数据库配置
database:
  host: "localhost"
  port: 3306
  user: "root"
  password: "root"
  database: "qgydb"

# 服务器配置
server:
  port: 9006
  log_level: "INFO"
EOF
fi

# 创建启动脚本
echo "📜 创建启动脚本..."
cat > start_server.sh << 'EOF'
#!/bin/bash

echo "🚀 启动AgentQL WebServer..."

# 激活虚拟环境
source venv/bin/activate

# 设置环境变量（可选）
# export OPENAI_API_KEY="your_key_here"
# export AGENTQL_API_KEY="your_key_here"

# 启动服务器
./server
EOF

chmod +x start_server.sh

echo ""
echo "🎉 安装完成！"
echo "=================================="
echo "📋 下一步操作："
echo "1. 配置数据库（可选）："
echo "   sudo mysql_secure_installation"
echo "   sudo mysql -u root -p"
echo "   CREATE DATABASE qgydb;"
echo ""
echo "2. 设置API密钥（可选）："
echo "   export OPENAI_API_KEY='your_key'"
echo "   export AGENTQL_API_KEY='your_key'"
echo ""
echo "3. 启动服务器："
echo "   ./start_server.sh"
echo ""
echo "4. 访问聊天界面："
echo "   http://localhost:9006/chat.html"
echo ""
echo "📁 项目结构："
echo "   ├── server          # 编译后的服务器"
echo "   ├── start_server.sh # 启动脚本"
echo "   ├── venv/           # Python虚拟环境"
echo "   ├── cgi/            # Python CGI脚本"
echo "   └── config/         # 配置文件"
echo ""
echo "🔧 故障排除："
echo "   - 查看日志：tail -f /var/log/syslog"
echo "   - 检查端口：netstat -tlnp | grep 9006"
echo "   - 测试CGI：python3 cgi/ai_chat.py" 