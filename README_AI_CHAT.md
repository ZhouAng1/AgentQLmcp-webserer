# AI Chat Assistant - TinyWebServer Pro

## 功能概述

这是一个集成到TinyWebServer的AI聊天助手，支持多种大语言模型，提供类似ChatGPT的对话体验。

## 主要特性

### 🤖 多模型支持
- **OpenAI GPT-3.5 Turbo**: 快速响应，适合一般对话
- **Anthropic Claude**: 深度理解，适合复杂问题
- **DeepSeek**: 中文优化，适合中文对话

### 💬 智能对话
- 持久化会话管理
- 对话历史记录
- 上下文理解
- 个性化回复

### 🎨 现代化界面
- 响应式设计
- 实时消息显示
- 模型切换功能
- 优雅的加载动画

## 文件结构

```
TinyWebServer/
├── root/
│   └── chat.html              # AI聊天界面
├── cgi/
│   ├── ai_chat.py            # 主要CGI脚本
│   ├── session_manager.py    # 会话管理
│   └── requirements.txt      # Python依赖
├── config/
│   └── ai_chat_config.yaml   # 配置文件
└── README_AI_CHAT.md         # 本说明文档
```

## 安装配置

### 1. 环境准备

```bash
# 安装Python依赖
pip install requests

# 设置环境变量（可选，也可以在代码中直接配置）
export OPENAI_API_KEY="your-openai-key"
export ANTHROPIC_API_KEY="your-anthropic-key"
export DEEPSEEK_API_KEY="your-deepseek-key"
```

### 2. 文件部署

```bash
# 确保CGI脚本有执行权限
chmod +x cgi/ai_chat.py
chmod +x cgi/session_manager.py

# 创建数据库目录
mkdir -p data
```

### 3. 服务器配置

确保TinyWebServer支持CGI执行：

```cpp
// 在webserver.cpp中确保CGI支持已启用
// 检查CGI路径配置
// 确保Python解释器路径正确
```

## 使用方法

### 1. 启动服务器

```bash
# 编译并启动TinyWebServer
make
./server
```

### 2. 访问聊天界面

在浏览器中访问：
```
http://localhost:9006/chat.html
```

### 3. 开始对话

1. 选择想要使用的AI模型
2. 在输入框中输入问题
3. 点击发送或按Enter键
4. 等待AI回复

## 配置说明

### 模型配置

在`config/ai_chat_config.yaml`中可以配置：

```yaml
ai_models:
  gpt-3.5-turbo:
    enabled: true
    api_key_env: OPENAI_API_KEY
    max_tokens: 1000
    temperature: 0.7
```

### 安全配置

```yaml
security:
  rate_limit_per_minute: 10      # 每分钟请求限制
  max_message_length: 1000       # 最大消息长度
  allowed_models: ["gpt-3.5-turbo", "claude", "deepseek"]
```

### 会话配置

```yaml
session:
  timeout_hours: 24              # 会话超时时间
  cleanup_days: 7                # 自动清理天数
  max_messages_per_session: 100  # 每会话最大消息数
```

## API接口

### 聊天接口

**POST** `/cgi/ai_chat.py`

请求体：
```json
{
  "message": "用户消息",
  "model": "gpt-3.5-turbo",
  "session_id": "会话ID（可选）"
}
```

响应：
```json
{
  "success": true,
  "response": "AI回复内容",
  "model": "使用的模型",
  "session_id": "会话ID",
  "usage": {
    "prompt_tokens": 10,
    "completion_tokens": 20,
    "total_tokens": 30
  }
}
```

## 数据库结构

### sessions表
- `session_id`: 会话唯一标识
- `created_at`: 创建时间
- `last_activity`: 最后活动时间

### messages表
- `id`: 消息ID
- `session_id`: 会话ID
- `role`: 角色（user/assistant）
- `content`: 消息内容
- `timestamp`: 时间戳

## 性能优化

### 1. 缓存策略
- 会话数据缓存
- 模型响应缓存
- 静态资源缓存

### 2. 并发处理
- 异步API调用
- 连接池管理
- 请求队列

### 3. 资源管理
- 自动清理过期会话
- 内存使用监控
- 错误重试机制

## 故障排除

### 常见问题

1. **CGI脚本无法执行**
   - 检查文件权限
   - 确认Python路径
   - 查看服务器日志

2. **API调用失败**
   - 检查API密钥配置
   - 确认网络连接
   - 查看错误日志

3. **数据库错误**
   - 检查数据库文件权限
   - 确认SQLite支持
   - 查看数据库日志

### 日志查看

```bash
# 查看AI聊天日志
tail -f ai_chat.log

# 查看服务器日志
tail -f server.log
```

## 扩展功能

### 1. 用户认证
- 用户注册/登录
- 权限管理
- 使用统计

### 2. 高级功能
- 文件上传/下载
- 图片生成
- 语音识别

### 3. 监控分析
- 使用统计
- 性能监控
- 错误分析

## 安全考虑

1. **API密钥安全**
   - 使用环境变量
   - 定期轮换密钥
   - 访问日志记录

2. **输入验证**
   - 消息长度限制
   - 内容过滤
   - SQL注入防护

3. **会话安全**
   - 会话超时
   - 自动清理
   - 访问控制

## 贡献指南

欢迎提交Issue和Pull Request来改进这个项目！

### 开发环境设置

```bash
# 克隆项目
git clone <repository-url>

# 安装依赖
pip install -r cgi/requirements.txt

# 运行测试
python cgi/session_manager.py
```

## 许可证

本项目遵循MIT许可证。

## 更新日志

### v1.0.0
- 初始版本发布
- 支持多模型对话
- 会话管理功能
- 现代化Web界面 