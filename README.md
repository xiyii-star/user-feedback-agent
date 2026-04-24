# 用户反馈智能处理系统

基于 LangChain 的用户反馈自动处理系统，支持分类、情绪识别、知识检索、回复生成、人工转接和处理归档。

## 核心流程

```
用户反馈输入
    ↓
【步骤1：理解阶段】
    ├─ 调用 classify 工具：反馈分类（咨询/投诉/建议/Bug/辱骂/广告）
    ├─ 调用 sentiment 工具：情绪识别（正常/不满/愤怒）
    └─ 调用 extract 工具：信息抽取（订单号、设备、联系方式等）
    ↓
【步骤2：知识检索】
    └─ 调用 rag_search 工具：在知识库中检索相关内容（FAQ/规则/案例）
    ↓
【步骤3：生成回复】
    └─ ReplyAgent 根据分类、情绪、检索结果生成客服回复
    ↓
【步骤4：决策执行】
    ├─ ExecutionAgent 判断是否需要转人工
    ├─ 如需转接：调用 transfer_human 工具，设置优先级
    └─ 生成处理动作建议
    ↓
【步骤5：保存归档】
    ├─ 调用 save_report 工具：保存完整处理报告到 data/reports/
    ├─ 更新会话记忆：记录当前对话
    └─ 更新用户历史：记录投诉次数、分类统计
    ↓
返回结构化处理结果
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
│   ├── memory.py          # 记忆管理
│   └── template_manager.py # Command & Skill 管理器
├── tools/
│   ├── classify.py        # 反馈分类
│   ├── sentiment.py       # 情绪识别
│   ├── extract.py         # 信息抽取
│   ├── rag.py            # RAG 检索
│   ├── transfer.py       # 人工转接
│   └── report.py         # 报告保存
├── commands/              # 用户命令模板（Markdown）
│   ├── summarize.md      # 反馈总结命令
│   └── analyze_trend.md  # 趋势分析命令
├── skills/                # Agent 技能模板（Markdown）
│   ├── suggest_solution.md  # 解决方案推荐
│   └── escalate_check.md    # 升级检查
├── knowledge/
│   ├── faq.txt           # FAQ 知识库
│   ├── rules.txt         # 平台规则
│   └── cases.txt         # 历史案例
└── data/
    ├── reports/          # 处理报告（自动生成）
    └── memory/           # 用户记忆（自动生成）
```

## 核心模块

| 模块                     | 说明                                                                                                                     |
| ------------------------ | ------------------------------------------------------------------------------------------------------------------------ |
| **MainAgent**      | 主编排器，负责整体流程控制、工具调用决策与子代理协调                                                                     |
| **SubAgents**      | 三个专业子代理：理解子代理（分类/情绪/抽取）、回复子代理（生成客服回复）、执行子代理（转人工判断）                       |
| **Memory**         | 双层记忆管理：会话记忆（当前对话上下文）+ 用户历史（投诉记录、重复用户识别），本地 JSON 持久化                           |
| **Tools**          | 可插拔工具集：反馈分类、情绪识别、信息抽取、RAG 检索、人工转接、报告保存，通过 LangChain Tool 接口统一注册               |
| **RAG**            | 完整的检索增强生成流水线：文档加载 → 文本分块 → 向量化（OpenAI Embeddings）→ FAISS 向量存储 → 语义检索 → 上下文生成 |
| **Knowledge Base** | 三类知识库：FAQ（常见问题）、Rules（平台规则）、Cases（历史案例），支持动态更新与自动索引                                |
| **Command & Skill** | Markdown 驱动的 Prompt 模板机制：Command 由用户主动调用，Skill 注册为 Tool 由 Agent 决策调用                           |

### 模块详解

#### 1. MainAgent（主编排器）

**核心机制**：

- 接收用户反馈和用户ID
- 按顺序调用工具完成理解、检索、回复、决策、归档
- 协调三个子代理的工作
- 管理记忆的读取和更新

**关键方法**：

```python
process_feedback(feedback: str, user_id: str) -> Dict
    ├─ 加载用户历史上下文
    ├─ 调用理解工具（classify, sentiment, extract）
    ├─ 调用 RAG 检索
    ├─ 调用 ReplyAgent 生成回复
    ├─ 调用 ExecutionAgent 判断转人工
    ├─ 保存报告
    └─ 更新记忆
```

#### 2. SubAgents（子代理）

**UnderstandingAgent（理解子代理）**：

- 职责：整合分类、情绪、信息抽取结果
- 输入：用户反馈 + 工具调用结果
- 输出：结构化的理解结果字典

**ReplyAgent（回复子代理）**：

- 职责：生成客服回复内容
- 核心机制：
  - 使用 ChatPromptTemplate 构建提示词
  - 输入：反馈内容、分类、情绪、RAG 检索结果
  - 通过 LLM 生成友好、专业的回复
  - 根据分类和情绪调整回复语气
- 输出：客服回复文本

**ExecutionAgent（执行子代理）**：

- 职责：判断是否转人工、生成处理动作
- 核心决策逻辑：
  ```
  辱骂/广告 → 不转人工，直接拒绝
  愤怒 + 投诉 → 转人工（紧急优先级）
  不满 + 投诉 → 转人工（高优先级）
  重复投诉用户 → 转人工（高优先级）
  Bug 类问题 → 转人工（普通优先级）
  其他 → 自动处理
  ```
- 输出：(是否转接, 转接原因, 优先级)

#### 3. Memory（记忆管理）

**双层记忆架构**：

**会话记忆（Session Memory）**：

- 存储：内存中的列表
- 内容：当前对话的所有反馈和处理结果
- 用途：提供上下文连续性
- 生命周期：程序运行期间

**用户历史（User History）**：

- 存储：`data/memory/{user_id}.json`
- 内容：
  ```json
  {
    "user_id": "user001",
    "total_feedbacks": 5,
    "complaint_count": 2,
    "transfer_count": 1,
    "categories": {"投诉": 2, "咨询": 3},
    "last_feedback_time": "2024-04-24 15:30:00"
  }
  ```
- 用途：识别重复投诉用户、统计用户行为
- 生命周期：持久化存储

**核心方法**：

```python
get_user_context(user_id) → 返回用户历史摘要
add_session_memory(feedback, result) → 添加会话记忆
update_user_history(user_id, category, transferred) → 更新用户历史
get_session_summary() → 获取会话摘要
```

#### 4. Tools（工具集）

所有工具通过 `@tool` 装饰器注册为 LangChain Tool，统一接口调用。

**classify（反馈分类）**：

- 机制：基于关键词匹配
- 分类：咨询、投诉、建议、Bug、辱骂、广告
- 实现：预定义关键词列表，优先级匹配

**sentiment（情绪识别）**：

- 机制：基于情绪关键词
- 分类：正常、不满、愤怒
- 实现：愤怒词 > 不满词 > 正常

**extract（信息抽取）**：

- 机制：正则表达式提取
- 提取内容：订单号、手机号、邮箱、设备型号
- 输出：结构化字典

**rag_search（RAG 检索）**：

- 机制：向量相似度检索
- 流程：
  ```
  初始化（首次调用）：
    ├─ 读取 knowledge/ 目录下的 txt 文件
    ├─ 文本分块（chunk_size=500, overlap=50）
    ├─ 向量化（OpenAI Embeddings）
    └─ 构建 FAISS 索引

  检索（每次调用）：
    ├─ 查询向量化
    ├─ FAISS 相似度搜索（top_k=3）
    └─ 返回相关文档片段
  ```

**transfer_human（人工转接）**：

- 机制：模拟转接流程
- 输入：转接原因、优先级（urgent/high/normal/low）
- 输出：转接确认信息

**save_report（报告保存）**：

- 机制：JSON 文件持久化
- 路径：`data/reports/report_{timestamp}.json`
- 内容：完整的处理结果字典

#### 5. RAG（检索增强生成）

**完整流水线**：

```
【初始化阶段】（首次调用时执行）
1. 文档加载
   └─ 读取 knowledge/faq.txt, rules.txt, cases.txt

2. 文档分块
   └─ CharacterTextSplitter(chunk_size=500, overlap=50)
   └─ 按段落分割，保持语义完整性

3. 向量化
   └─ OpenAI Embeddings API
   └─ 每个文本块转换为 1536 维向量

4. 向量存储
   └─ FAISS.from_texts() 构建索引
   └─ 内存中维护向量数据库

【检索阶段】（每次调用时执行）
1. 查询向量化
   └─ 用户反馈转换为向量

2. 相似度检索
   └─ FAISS.similarity_search(query, k=3)
   └─ 返回最相关的 3 个文档片段

3. 结果格式化
   └─ 附加来源信息（faq/rules/cases）
   └─ 返回格式化的检索结果
```

**优化机制**：

- 全局单例：向量数据库只初始化一次
- 分块策略：保持语义完整性，避免截断
- 元数据管理：记录每个片段的来源文件

#### 6. Knowledge Base（知识库）

**三类知识**：

**faq.txt（常见问题）**：

- 内容：用户常见问题和标准答案
- 格式：问题 + 答案对
- 用途：快速响应常见咨询

**rules.txt（平台规则）**：

- 内容：平台使用规范、违规处理标准
- 用途：处理投诉、辱骂、广告等违规内容

**cases.txt（历史案例）**：

- 内容：典型问题的处理案例
- 用途：参考历史经验，提供解决方案

**更新机制**：

- 修改 txt 文件后，下次运行自动重建向量索引
- 支持动态添加新知识，无需修改代码

#### 7. Command & Skill（命令与技能系统）

**核心机制**：基于 Markdown + YAML Frontmatter 的 Prompt 模板系统

**Command（用户命令）**：

- 存储位置：`commands/` 目录
- 调用方式：用户主动输入 `/命令名`
- 用途：提供快捷操作，如总结、分析趋势等
- 模板格式：
  ```markdown
  ---
  name: summarize
  description: 总结用户反馈的核心问题
  trigger: /summarize
  inputs:
    - feedback
  ---
  
  # 反馈总结
  
  请对以下用户反馈进行总结...
  {feedback}
  ```

**Skill（Agent 技能）**：

- 存储位置：`skills/` 目录
- 调用方式：注册为 LangChain Tool，由 Agent 自主决策调用
- 用途：扩展 Agent 能力，如解决方案推荐、升级检查等
- 模板格式：
  ```markdown
  ---
  name: suggest_solution
  description: 根据反馈内容智能推荐解决方案
  category: skill
  inputs:
    - feedback
    - category
    - knowledge
  ---
  
  # 解决方案推荐
  
  根据用户反馈和知识库，推荐最合适的解决方案...
  ```

**工作流程**：

```
【Command 流程】
用户输入 /summarize
    ↓
CommandManager 加载 summarize.md 模板
    ↓
填充输入参数（feedback）
    ↓
调用 LLM 执行 Prompt
    ↓
返回结果给用户

【Skill 流程】
SkillManager 扫描 skills/ 目录
    ↓
将每个 Skill 注册为 @tool
    ↓
Agent 根据任务需求决策调用
    ↓
Skill Tool 填充参数并执行
    ↓
返回结果给 Agent
```

**管理器**：

- **TemplateLoader**：解析 Markdown 模板，提取 YAML frontmatter 和 prompt
- **CommandManager**：管理用户命令，提供 `execute_command()` 方法
- **SkillManager**：管理 Agent 技能，提供 `register_skills_as_tools()` 方法

**扩展方式**：

1. 创建新的 `.md` 文件到 `commands/` 或 `skills/` 目录
2. 定义 YAML frontmatter（name, description, inputs）
3. 编写 Prompt 模板（支持 `{变量}` 占位符）
4. 重启系统自动加载

**使用示例**：

```bash
# 交互模式中使用命令
[user001] 请输入用户反馈: /summarize

# 查看可用命令
[user001] 请输入用户反馈: commands

# 查看可用技能
[user001] 请输入用户反馈: skills
```

## 核心能力

1. **智能分类**：自动识别咨询/投诉/建议/Bug/辱骂/广告
2. **情绪识别**：判断用户情绪（正常/不满/愤怒）
3. **RAG 检索**：基于 FAISS 向量数据库检索知识库
4. **智能回复**：根据检索结果生成客服回复
5. **转人工判断**：根据分类、情绪、历史自动决策
6. **轻量记忆**：会话记忆 + 用户历史，本地 JSON 持久化
7. **命令系统**：用户可通过 `/命令` 快速执行预定义操作
8. **技能扩展**：通过 Markdown 模板轻松扩展 Agent 能力

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

### 添加自定义命令

在 `commands/` 目录创建新的 `.md` 文件：

```markdown
---
name: my_command
description: 我的自定义命令
trigger: /my_command
inputs:
  - param1
  - param2
---

# 命令标题

你的 Prompt 模板内容...
使用 {param1} 和 {param2} 作为占位符
```

### 添加自定义技能

在 `skills/` 目录创建新的 `.md` 文件：

```markdown
---
name: my_skill
description: 我的自定义技能
category: skill
inputs:
  - input1
  - input2
---

# 技能标题

你的 Prompt 模板内容...
使用 {input1} 和 {input2} 作为占位符
```

重启系统后自动加载新的命令和技能。

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
