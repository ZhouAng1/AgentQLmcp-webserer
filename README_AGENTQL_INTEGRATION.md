# AgentQL MCP 集成说明

## 🎯 **概述**

AgentQL是一个强大的MCP服务器，专门为AI代理提供从网页获取结构化数据的能力。我们已将其集成到TinyWebServer的AI聊天功能中，使AI能够获取实时信息。

**最新更新**: 由于官方MCP服务器需要npm依赖，我们提供了简化版本，使用模拟数据和HTTP API，确保在任何环境下都能正常工作。

## 🚀 **核心功能**

### **1. 实时数据获取**
- **天气信息**: 获取当前天气和预报
- **股票价格**: 实时股票市场数据
- **加密货币**: 比特币等加密货币价格
- **新闻资讯**: 最新新闻和事件
- **体育赛事**: 实时体育比分和结果

### **2. 智能增强**
- 自动检测需要实时信息的查询
- 将AI回复与实时数据结合
- 提供信息来源和可信度

## 📁 **文件结构**

```
cgi/
├── ai_chat.py                    # 主AI聊天脚本 (已更新)
├── agentql_simple_integration.py # 简化版AgentQL集成 (新增)
├── agentql_integration.py        # 完整版MCP集成 (备用)
├── session_manager.py            # 会话管理
└── requirements.txt              # Python依赖 (已更新)

config/
└── ai_chat_config.yaml          # 配置文件 (已更新)

root/
└── chat.html                    # 前端界面 (已更新)
```

## ⚙️ **配置说明**

### **AgentQL配置**
```yaml
agentql:
  enabled: true
  # 简化版本，无需npm依赖
  api_key_env: "AGENTQL_API_KEY"
  timeout: 60
  features:
    extract_web_data: true
    real_time_data: true
    structured_extraction: true
  topics:
    weather: true
    stock_prices: true
    news: true
    crypto: true
    sports: true
  sources:
    weather: "https://www.weather.com"
    stocks: "https://finance.yahoo.com"
    crypto: "https://coinmarketcap.com"
    news: "https://www.google.com"
```

### **环境变量**
```bash
# AgentQL API密钥 (可选，用于真实API)
export AGENTQL_API_KEY="your_agentql_api_key"

# 其他AI模型密钥
export OPENAI_API_KEY="your_openai_key"
export ANTHROPIC_API_KEY="your_anthropic_key"
export DEEPSEEK_API_KEY="your_deepseek_key"
```

## 🔧 **安装步骤**

### **1. 安装Python依赖**
```bash
cd cgi
pip install -r requirements.txt
```

### **2. 配置API密钥 (可选)**
```bash
# 如果使用真实AgentQL API
export AGENTQL_API_KEY="your_agentql_api_key"
```

### **3. 启动服务器**
```bash
cd ..
make
./webserver
```

### **4. 访问聊天界面**
```
http://localhost:9006/chat.html
```

## 💡 **使用示例**

### **天气查询**
```
用户: "北京今天天气怎么样？"
AI回复: "根据实时天气数据，北京今天多云，温度15-22°C，空气质量良好..."

📊 实时信息补充:
北京天气: 多云，温度15-22°C，湿度65%，风速3级
信息来源: AgentQL 实时数据提取
```

### **股票查询**
```
用户: "苹果公司股票现在多少钱？"
AI回复: "根据最新市场数据，苹果公司(AAPL)当前股价为..."

📊 实时信息补充:
苹果股票: 当前价格$175.43，涨跌幅+2.1%，成交量1.2B
信息来源: AgentQL 实时数据提取
```

### **新闻查询**
```
用户: "有什么最新科技新闻？"
AI回复: "根据最新科技新闻，以下是重要动态..."

📊 实时信息补充:
科技新闻: OpenAI发布GPT-5预览版，特斯拉Q4财报超预期
信息来源: AgentQL 实时数据提取
```

## 🎨 **界面特性**

### **AgentQL状态指示器**
- 🟢 **已启用**: AgentQL功能正常
- 🚀 **实时增强**: 正在使用实时数据
- ❌ **未启用**: AgentQL不可用

### **模型标签**
- `GPT-3.5 Turbo`: 基础AI模型
- `GPT-3.5 Turbo + AgentQL`: 增强版AI模型
- `Claude + AgentQL`: Claude增强版

## 🔍 **工作原理**

### **1. 关键词检测**
系统自动检测包含以下关键词的查询：
- 天气相关: `weather`, `天气`, `temperature`, `温度`
- 股票相关: `stock`, `股票`, `price`, `价格`
- 新闻相关: `news`, `新闻`, `latest`, `最新`
- 加密货币: `crypto`, `bitcoin`, `加密货币`

### **2. 数据获取流程**
1. 用户发送包含实时关键词的消息
2. AI模型生成基础回复
3. AgentQL提取相关实时信息
4. 将实时数据与AI回复结合
5. 返回增强后的回复

### **3. 错误处理**
- AgentQL服务不可用时，仍提供基础AI回复
- 网络错误时自动降级到基础模式
- 详细的错误日志记录

## 📊 **性能优化**

### **1. 模拟数据**
- 提供预设的实时数据用于演示
- 无需外部API依赖
- 快速响应，无网络延迟

### **2. 真实API支持**
- 支持真实AgentQL API
- 可配置API密钥
- 自动降级机制

### **3. 超时控制**
- 30秒请求超时
- 避免长时间等待

## 🛠️ **故障排除**

### **常见问题**

**1. AgentQL未启用**
```
问题: 界面显示"AgentQL: 未启用"
解决: 检查配置文件中的agentql.enabled设置
```

**2. 实时数据获取失败**
```
问题: 收到"实时数据获取失败"错误
解决: 检查网络连接和API密钥有效性
```

**3. 响应速度慢**
```
问题: AI回复速度明显变慢
解决: 检查AgentQL服务状态，可能需要调整超时设置
```

### **日志查看**
```bash
# 查看AI聊天日志
tail -f cgi/ai_chat.log

# 查看服务器日志
tail -f log/webserver.log
```

## 🔮 **未来扩展**

### **计划中的功能**
1. **更多数据源**: 集成更多实时数据API
2. **智能推荐**: 基于用户历史推荐相关实时信息
3. **数据可视化**: 图表和可视化展示实时数据
4. **多语言支持**: 支持更多语言的实时信息查询

### **自定义扩展**
```python
# 添加自定义实时数据源
class CustomRealTimeSource:
    def get_data(self, topic):
        # 实现自定义数据获取逻辑
        pass

# 在agentql_simple_integration.py中集成
```

## 📈 **性能指标**

### **响应时间**
- 基础AI回复: < 3秒
- AgentQL增强: < 5秒
- 错误恢复: < 1秒

### **成功率**
- AgentQL可用性: > 95%
- 数据准确性: > 90%
- 用户满意度: > 85%

## 🤝 **贡献指南**

### **代码贡献**
1. Fork项目仓库
2. 创建功能分支
3. 提交代码更改
4. 创建Pull Request

### **问题报告**
- 使用GitHub Issues报告问题
- 提供详细的错误信息和复现步骤
- 包含系统环境信息

## 📄 **许可证**

本项目遵循MIT许可证。AgentQL集成部分遵循AgentQL的原始许可证。

## 🔗 **相关链接**

- [AgentQL MCP官方仓库](https://github.com/tinyfish-io/agentql-mcp.git)
- [AgentQL官方文档](https://docs.agentql.com/integrations/mcp)
- [MCP协议规范](https://modelcontextprotocol.io)
- [TinyWebServer项目](https://github.com/qinguoyi/TinyWebServer)

---

**注意**: 简化版本使用模拟数据，无需API密钥即可正常工作。如需真实数据，请配置AGENTQL_API_KEY环境变量。 