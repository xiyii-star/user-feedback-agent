# 项目结构

```
userFeedback/
├── main.py                          # CLI入口
├── requirements.txt                 # 依赖包
├── .env.example                     # 环境变量示例
├── README.md                        # 项目说明
├── USAGE.md                         # 使用指南
├── test_feedbacks.json              # 测试用例
│
├── agent/                           # Agent模块
│   ├── __init__.py
│   ├── main_agent.py               # 主Agent（编排决策）
│   ├── sub_agents.py               # 子代理（理解/回复/执行）
│   └── memory.py                   # 记忆管理
│
├── tools/                           # 工具模块
│   ├── __init__.py
│   ├── classify.py                 # 反馈分类工具
│   ├── sentiment.py                # 情绪识别工具
│   ├── extract.py                  # 信息抽取工具
│   ├── rag.py                      # RAG检索工具
│   ├── transfer.py                 # 人工转接工具
│   └── report.py                   # 报告保存工具
│
├── knowledge/                       # 知识库
│   ├── faq.txt                     # FAQ知识
│   ├── rules.txt                   # 平台规则
│   └── cases.txt                   # 历史案例
│
└── data/                            # 数据存储
    ├── reports/                    # 处理报告（自动生成）
    └── memory/                     # 用户记忆（自动生成）
```

## 核心文件说明

### 入口文件
- **main.py**: CLI主程序，支持交互模式、单条处理、批量处理

### Agent模块
- **main_agent.py**: 主Agent，负责整体流程编排和工具调用
- **sub_agents.py**: 三个子代理（理解/回复/执行），模块化处理
- **memory.py**: 记忆管理，包含会话记忆和用户历史

### 工具模块
- **classify.py**: 基于关键词的反馈分类（咨询/投诉/建议/Bug/辱骂/广告）
- **sentiment.py**: 情绪识别（正常/不满/愤怒）
- **extract.py**: 正则提取订单号、设备、联系方式等
- **rag.py**: 基于FAISS的向量检索
- **transfer.py**: 人工转接逻辑
- **report.py**: JSON格式报告保存

### 知识库
- **faq.txt**: 10个常见问题和答案
- **rules.txt**: 8条平台规则
- **cases.txt**: 8个历史处理案例

## 数据流

```
用户输入 → main.py
    ↓
MainAgent.process_feedback()
    ↓
1. 调用工具: classify + sentiment + extract
2. RAG检索: rag_search
3. 生成回复: ReplyAgent
4. 判断转接: ExecutionAgent
5. 保存报告: save_report
6. 更新记忆: UserMemory
    ↓
返回结构化结果
```
