# AI 聊天 Web 服务器

基于C++的高性能Web服务器，集成DeepSeek AI聊天功能。

## 🚀 快速启动

```bash
# 克隆项目
git clone https://github.com/ZhouAng1/AgentQLmcp-webserer.git
cd AgentQLmcp-webserer

# 安装依赖
sudo apt update
sudo apt install -y python3 python3-pip mysql-server mysql-client g++ make

# 设置MySQL
sudo mysql -e "ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'root'; FLUSH PRIVILEGES;"

# 启动服务器
chmod +x run.sh
./run.sh
```

## 🌐 访问

打开浏览器访问：http://localhost:9006/chat.html

## 📁 核心文件

- `main.cpp` - 主程序
- `cgi/ai_chat.py` - AI聊天处理
- `root/chat.html` - 聊天界面
- `run.sh` - 启动脚本

## 🔧 功能

- ✅ AI聊天对话
- ✅ 会话历史记录
- ✅ 实时日志
- ✅ 一键启动

---

**注意**: 确保在项目根目录运行启动脚本。

