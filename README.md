# AI 聊天 Web 服务器

基于C++的高性能Web服务器，集成DeepSeek AI聊天功能。

## ⚠️ 重要提示

**使用前请配置你的DeepSeek API密钥！**

1. 获取API密钥：访问 [DeepSeek官网](https://platform.deepseek.com/) 注册并获取API密钥
2. 配置API密钥：编辑 `run.sh` 文件，将 `your_deepseek_api_key_here` 替换为你的实际API密钥

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

# 配置API密钥
# 编辑 run.sh 文件，将 your_deepseek_api_key_here 替换为你的实际API密钥

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

## 🔑 API配置

### DeepSeek API密钥配置

1. **获取API密钥**
   - 访问 [DeepSeek官网](https://platform.deepseek.com/)
   - 注册账户并获取API密钥

2. **配置API密钥**
   ```bash
   # 编辑启动脚本
   nano run.sh
   
   # 将以下行中的占位符替换为你的实际API密钥
   export DEEPSEEK_API_KEY="your_deepseek_api_key_here"
   ```

3. **验证配置**
   ```bash
   # 测试API密钥
   export DEEPSEEK_API_KEY="your_actual_key"
   echo '{"message":"test"}' | CONTENT_LENGTH=20 python3 root/cgi/ai_chat.py
   ```

---

**注意**: 确保在项目根目录运行启动脚本。

