# 用户反馈智能处理系统

基于 LangChain 的用户反馈自动处理系统，支持分类、情绪识别、知识检索、回复生成、人工转接和处理归档。

## 核心流程

```
用户反馈 → 分类/情绪/信息抽取 → RAG 检索 → 生成回复 → 判断是否转人工 → 保存处理报告
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```env
OPENAI_API_KEY=sk-your-api-key-here
OPENAI_API_BASE=https://api.openai.com/v1
MODEL_NAME=gpt-4
```

### 3. 运行系统

**交互模式**：
```bash
python main.py
```

**单条处理**：
```bash
python main.py --feedback "我的订单123456还没发货，催了两次没人理" --user-id user001
```

**批量处理**：
```bash
python main.py --batch test_feedbacks.json
```

## 项目结构

```
user-feedback-agent/
├── main.py                 # CLI 入口
├── requirements.txt        # 依赖包
├── .env.example           # 环境变量示例
├── test_feedbacks.json    # 测试用例
├── agent/
│   ├── main_agent.py      # 主 Agent 编排
│   ├── sub_agents.py      # 子代理（理解/回复/执行）
│   └── memory.py          # 记忆管理
├── tools/
│   ├── classify.py        # 反馈分类
│   ├── sentiment.py       # 情绪识别
│   ├── extract.py         # 信息抽取
│   ├── rag.py            # RAG 检索
│   ├── transfer.py       # 人工转接
│   └── report.py         # 报告保存
├── knowledge/
│   ├── faq.txt           # FAQ 知识库
│   ├── rules.txt         # 平台规则
│   └── cases.txt         # 历史案例
└── data/
    ├── reports/          # 处理报告（自动生成）
    └── memory/           # 用户记忆（自动生成）
```

## 核心能力

1. **智能分类**：自动识别咨询/投诉/建议/Bug/辱骂/广告
2. **情绪识别**：判断用户情绪（正常/不满/愤怒）
3. **RAG 检索**：基于 FAISS 向量数据库检索知识库
4. **智能回复**：根据检索结果生成客服回复
5. **转人工判断**：根据分类、情绪、历史自动决策
6. **轻量记忆**：会话记忆 + 用户历史，本地 JSON 持久化

## 输出示例

输入：
```
我的订单123456还没发货，催了两次没人理，太离谱了
```

输出：
```json
{
  "用户反馈": "我的订单123456还没发货，催了两次没人理，太离谱了",
  "分类": "投诉",
  "情绪": "愤怒",
  "抽取信息": {
    "订单号": "123456",
    "问题摘要": "订单未发货且客服未响应"
  },
  "处理动作": "转人工处理",
  "是否转人工": true,
  "转接信息": "已转接人工客服 | 原因: 用户情绪激烈的投诉 | 优先级: 紧急",
  "回复内容": "非常抱歉给您带来不便...",
  "处理报告": "已保存至: data/reports/report_xxx.json"
}
```

## 测试用例

系统提供了 6 个测试用例（`test_feedbacks.json`）：

1. **投诉类**：订单未发货 + 愤怒情绪 → 转人工
2. **Bug类**：App闪退 → 转技术团队
3. **建议类**：功能建议 → 记录并感谢
4. **辱骂类**：恶意辱骂 → 警告拒绝
5. **广告类**：商业推广 → 删除警告
6. **重复投诉**：同一用户再次投诉 → 高优先级转人工

## 自定义配置

### 修改知识库

编辑 `knowledge/` 目录下的文件，系统会自动重新构建向量数据库。

### 调整转人工规则

编辑 `agent/sub_agents.py` 中的 `ExecutionAgent.should_transfer()` 方法。

### 修改分类规则

编辑 `tools/classify.py` 中的关键词列表。

## 常见问题

**Q: 如何使用国内API服务？**

A: 修改 `.env` 文件中的 `OPENAI_API_BASE`，例如：
- 智谱AI：`https://open.bigmodel.cn/api/paas/v4/`
- 通义千问：`https://dashscope.aliyuncs.com/compatible-mode/v1`

**Q: 如何查看处理报告？**

A: 所有报告保存在 `data/reports/` 目录，JSON格式。

**Q: 如何清空用户记忆？**

A: 删除 `data/memory/` 目录下的对应用户文件。

## 支持场景

1. **内容社区**：评论 / 私信 / 举报 / 建议
2. **电商售后**：发货、退款、质量、客服投诉
