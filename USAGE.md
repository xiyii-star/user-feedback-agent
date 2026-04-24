# 用户反馈智能处理系统 - 使用指南

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置API Key

创建 `.env` 文件：

```bash
cp .env.example .env
```

编辑 `.env` 文件，填入你的配置：

```env
OPENAI_API_KEY=sk-your-api-key-here
OPENAI_API_BASE=https://api.openai.com/v1
MODEL_NAME=gpt-4
```

如果使用国内API服务（如智谱、通义千问等），修改 `OPENAI_API_BASE` 为对应的API地址。

### 3. 运行系统

#### 交互模式（推荐）

```bash
python main.py
```

进入交互模式后：
- 输入用户ID（可选，默认为 default）
- 输入用户反馈内容
- 输入 `history` 查看会话记忆
- 输入 `quit` 或 `exit` 退出

#### 单条反馈处理

```bash
python main.py --feedback "我的订单123456还没发货，催了两次没人理，太离谱了" --user-id user001
```

#### 批量处理

```bash
python main.py --batch test_feedbacks.json
```

## 测试用例

系统提供了 6 个测试用例（`test_feedbacks.json`）：

1. **投诉类**：订单未发货 + 愤怒情绪 → 转人工
2. **Bug类**：App闪退 → 转技术团队
3. **建议类**：功能建议 → 记录并感谢
4. **辱骂类**：恶意辱骂 → 警告拒绝
5. **广告类**：商业推广 → 删除警告
6. **重复投诉**：同一用户再次投诉 → 高优先级转人工

运行批量测试：

```bash
python main.py --batch test_feedbacks.json
```

## 系统架构

### 核心组件

1. **主Agent** (`agent/main_agent.py`)
   - 负责整体流程编排
   - 调用工具和子代理
   - 决策处理策略

2. **子代理** (`agent/sub_agents.py`)
   - 理解子代理：分类、情绪、信息抽取
   - 回复子代理：生成客服回复
   - 执行子代理：判断转人工、生成动作

3. **记忆系统** (`agent/memory.py`)
   - 会话记忆：当前对话历史
   - 用户记忆：历史投诉记录

4. **工具集** (`tools/`)
   - `classify.py`：反馈分类
   - `sentiment.py`：情绪识别
   - `extract.py`：信息抽取
   - `rag.py`：知识库检索
   - `transfer.py`：人工转接
   - `report.py`：报告保存

5. **知识库** (`knowledge/`)
   - `faq.txt`：常见问题
   - `rules.txt`：平台规则
   - `cases.txt`：历史案例

### 处理流程

```
用户反馈输入
    ↓
理解阶段（分类、情绪、信息抽取）
    ↓
知识检索（RAG）
    ↓
生成回复
    ↓
决策判断（是否转人工）
    ↓
保存报告 + 更新记忆
    ↓
输出结果
```

## 输出示例

```json
{
  "用户反馈": "我的订单123456还没发货，催了两次没人理，太离谱了",
  "分类": "投诉",
  "情绪": "愤怒",
  "抽取信息": {
    "订单号": "123456",
    "问题摘要": "我的订单123456还没发货，催了两次没人理，太离谱了"
  },
  "处理动作": "转人工处理",
  "是否转人工": true,
  "转接信息": "已转接人工客服 | 原因: 用户情绪激烈的投诉 | 优先级: 紧急",
  "回复内容": "非常抱歉给您带来不便。经查询，您的订单因仓库备货延迟...",
  "处理报告": "已保存至: data/reports/report_20260424_120000.json"
}
```

## 自定义配置

### 修改知识库

编辑 `knowledge/` 目录下的文件：
- `faq.txt`：添加常见问题和答案
- `rules.txt`：修改平台规则
- `cases.txt`：添加历史处理案例

修改后系统会自动重新构建向量数据库。

### 调整转人工规则

编辑 `agent/sub_agents.py` 中的 `ExecutionAgent.should_transfer()` 方法：

```python
def should_transfer(self, category: str, sentiment: str, user_context: str):
    # 自定义转人工逻辑
    if category == "投诉" and sentiment == "愤怒":
        return True, "用户情绪激烈", "urgent"
    # ...
```

### 修改分类规则

编辑 `tools/classify.py` 中的关键词列表：

```python
complaint_keywords = ["投诉", "太离谱", "没人理", ...]
```

## 常见问题

### Q: 如何使用国内API服务？

A: 修改 `.env` 文件中的 `OPENAI_API_BASE`，例如：
- 智谱AI：`https://open.bigmodel.cn/api/paas/v4/`
- 通义千问：`https://dashscope.aliyuncs.com/compatible-mode/v1`

同时修改 `MODEL_NAME` 为对应的模型名称。

### Q: 向量数据库初始化失败？

A: 确保：
1. 已安装 `faiss-cpu`
2. API Key 配置正确
3. 网络连接正常

### Q: 如何查看处理报告？

A: 所有报告保存在 `data/reports/` 目录，JSON格式，可直接查看。

### Q: 如何清空用户记忆？

A: 删除 `data/memory/` 目录下的对应用户文件。

## 项目特点

1. **单智能体架构**：主Agent统一编排，子代理模块化处理
2. **RAG增强**：基于FAISS的知识库检索
3. **轻量记忆**：会话记忆 + 用户历史，本地JSON持久化
4. **灵活工具**：6个核心工具，易于扩展
5. **智能决策**：根据分类、情绪、历史自动判断处理策略

## 扩展建议

1. **接入真实数据库**：替换JSON文件为MySQL/MongoDB
2. **接入消息队列**：处理高并发反馈
3. **增强RAG**：使用更大的向量数据库（Milvus/Pinecone）
4. **多模态支持**：处理图片、语音反馈
5. **实时监控**：添加处理统计和告警
