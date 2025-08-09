# AgentQL WebServer AI 聊天系统

一个基于C++的高性能Web服务器，集成了DeepSeek AI聊天功能。

## 🚀 快速开始

### 1. 环境要求
- Ubuntu 18.04+
- Python 3.8+
- MySQL 5.7+
- GCC 7.0+

### 2. 一键安装和启动

```bash
# 克隆项目
git clone https://github.com/ZhouAng1/AgentQLmcp-webserer.git
cd AgentQLmcp-webserer

# 安装依赖
sudo apt update
sudo apt install -y python3 python3-pip python3-venv python3-full mysql-server mysql-client g++ make

# 设置MySQL
sudo mysql -e "ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'root'; FLUSH PRIVILEGES;"

# 启动服务
chmod +x start.sh
./start.sh
```

### 3. 访问聊天界面
打开浏览器访问：http://localhost:9006/chat.html

## 🔧 功能特性

- ✅ 高性能C++ Web服务器
- ✅ DeepSeek AI聊天集成
- ✅ 会话管理和历史记录
- ✅ 实时日志记录
- ✅ 一键启动脚本
- ✅ 完整的错误处理

## 📁 项目结构

```
AgentQLmcp-webserer/
├── main.cpp                 # 主程序入口
├── webserver.h/cpp          # Web服务器核心
├── http/http_conn.h/cpp     # HTTP连接处理
├── cgi/ai_chat.py          # AI聊天CGI脚本
├── root/chat.html          # 聊天界面
├── start.sh                # 一键启动脚本
└── README.md               # 项目说明
```

## 🛠️ 故障排除

### 编译错误
```bash
# 清理并重新编译
make clean
make
```

### MySQL连接问题
```bash
# 检查MySQL服务
sudo systemctl status mysql

# 重启MySQL
sudo systemctl restart mysql

# 重置密码
sudo mysql -e "ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'root'; FLUSH PRIVILEGES;"
```

### 端口占用
```bash
# 检查端口
netstat -tlnp | grep 9006

# 杀死进程
sudo fuser -k 9006/tcp
```

### CGI测试
```bash
# 测试CGI脚本
chmod +x test_cgi.sh
./test_cgi.sh
```

## 📝 日志文件

- `ai_chat.log` - AI聊天日志
- 服务器日志在控制台输出

## 🔑 API配置

DeepSeek API Key已预配置在启动脚本中：
```bash
export DEEPSEEK_API_KEY="sk-7d3a5f1e93184ef8a00ab4e8c6fa6677"
```

## 🚀 开发

### 添加新功能
1. 修改 `cgi/ai_chat.py` 添加新的AI模型
2. 更新 `root/chat.html` 前端界面
3. 重新编译并测试

### 调试
```bash
# 查看详细日志
tail -f ai_chat.log

# 手动测试CGI
echo '{"message":"test"}' | CONTENT_LENGTH=20 python3 cgi/ai_chat.py
```

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交Issue和Pull Request！

---

**注意**: 确保在项目根目录运行所有脚本，并检查MySQL服务状态。

