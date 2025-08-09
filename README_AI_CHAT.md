# AgentQL WebServer AI 聊天系统

## 🎉 功能特性

- **🤖 DeepSeek AI 集成** - 基于 DeepSeek API 的智能对话
- **💬 实时聊天** - 流畅的对话体验
- **🔄 会话管理** - 自动保存对话历史
- **📱 响应式设计** - 支持桌面和移动设备
- **⚡ 高性能** - 基于 epoll 的高并发服务器

## 🚀 快速开始

### 1. 环境要求
- Ubuntu 20.04+ / CentOS 7+
- Python 3.7+
- MySQL 5.7+
- GCC 7+

### 2. 一键启动
```bash
# 给启动脚本执行权限
chmod +x start.sh

# 启动服务器
./start.sh
```

### 3. 访问聊天界面
打开浏览器访问：http://localhost:9006/chat.html

## 🔧 技术架构

### 后端架构
- **Web服务器**: 基于 epoll 的高性能 C++ 服务器
- **CGI处理**: Python CGI 脚本处理 AI 请求
- **数据库**: SQLite 存储会话数据
- **AI服务**: DeepSeek API 集成

### 前端架构
- **界面**: 现代化响应式聊天界面
- **通信**: AJAX 异步请求
- **样式**: CSS3 渐变和动画效果

## 📁 项目结构

```
AgentQLmcp-webserer/
├── main.cpp                 # 主程序入口
├── webserver.cpp           # 服务器核心逻辑
├── http/                   # HTTP 处理模块
│   ├── http_conn.cpp      # HTTP 连接处理
│   └── http_conn.h        # HTTP 连接头文件
├── cgi/                    # CGI 脚本目录
│   ├── ai_chat.py         # AI 聊天处理脚本
│   └── session_manager.py # 会话管理
├── root/                   # 静态文件目录
│   └── chat.html          # 聊天界面
├── config/                 # 配置文件目录
├── start.sh               # 一键启动脚本
└── README_AI_CHAT.md      # 本文档
```

## 🔑 API 配置

### DeepSeek API
系统已预配置 DeepSeek API 密钥：
```
DEEPSEEK_API_KEY=sk-7d3a5f1e93184ef8a00ab4e8c6fa6677
```

如需更换 API 密钥，请修改 `start.sh` 文件中的环境变量。

## 💻 使用示例

### 基本对话
```
用户: 你好，请介绍一下自己
AI: 你好！我是基于 DeepSeek 的 AI 助手。我可以帮助你回答问题、编写代码、分析问题等。请告诉我你需要什么帮助！
```

### 代码编写
```
用户: 请帮我写一个 Python 的快速排序算法
AI: 当然可以！以下是 Python 实现的快速排序算法：

def quicksort(arr):
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quicksort(left) + middle + quicksort(right)

# 使用示例
arr = [3, 6, 8, 10, 1, 2, 1]
sorted_arr = quicksort(arr)
print(sorted_arr)  # 输出: [1, 1, 2, 3, 6, 8, 10]
```

## 🛠️ 故障排除

### 常见问题

1. **编译失败**
   ```bash
   # 安装依赖
   sudo apt update
   sudo apt install build-essential g++ make python3 python3-pip
   ```

2. **端口被占用**
   ```bash
   # 查看端口占用
   sudo netstat -tlnp | grep 9006
   
   # 释放端口
   sudo fuser -k 9006/tcp
   ```

3. **CGI 脚本权限问题**
   ```bash
   # 设置执行权限
   chmod +x cgi/*.py
   ```

4. **API 调用失败**
   - 检查网络连接
   - 验证 API 密钥是否正确
   - 查看服务器日志

### 日志查看
```bash
# 查看系统日志
tail -f /var/log/syslog | grep server

# 查看 CGI 脚本日志
tail -f /var/log/syslog | grep python
```

## 🔒 安全说明

- API 密钥已硬编码在启动脚本中，生产环境请使用环境变量
- 建议配置防火墙限制端口访问
- 定期更新依赖包以修复安全漏洞

## 📈 性能优化

- 服务器支持高并发连接
- 使用连接池管理数据库连接
- 静态文件使用内存映射提高访问速度
- CGI 脚本使用进程池处理请求

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request 来改进项目！

## 📄 许可证

本项目采用 MIT 许可证。

---

**享受与 AI 的智能对话吧！** 🎉 