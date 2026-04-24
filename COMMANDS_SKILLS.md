# Command & Skill 系统使用指南

## 概述

Command & Skill 是基于 Markdown + YAML Frontmatter 的 Prompt 模板系统，提供两种扩展机制：

- **Command（命令）**：用户主动调用的快捷操作
- **Skill（技能）**：Agent 自主决策调用的能力扩展

## Command（命令）

### 什么是 Command？

Command 是用户可以直接调用的预定义操作，通过 `/命令名` 触发。

### 使用场景

- 快速总结反馈内容
- 分析反馈趋势
- 生成报告
- 数据统计

### 创建 Command

1. 在 `commands/` 目录创建 `.md` 文件
2. 定义 YAML frontmatter
3. 编写 Prompt 模板

### 模板格式

```markdown
---
name: 命令名称（英文，用于代码调用）
description: 命令描述（中文，显示给用户）
trigger: /命令触发词
inputs:
  - 参数1
  - 参数2
---

# Prompt 标题

这里是 Prompt 内容，可以使用 {参数1} 和 {参数2} 作为占位符。

系统会自动将参数值填充到这些位置。
```

### 示例：反馈总结命令

文件：`commands/summarize.md`

```markdown
---
name: summarize
description: 总结用户反馈的核心问题
trigger: /summarize
inputs:
  - feedback
---

# 反馈总结

请对以下用户反馈进行总结，提取核心问题和关键信息：

用户反馈：
```
{feedback}
```

请用简洁的语言总结：
1. 核心问题是什么
2. 用户的主要诉求
3. 涉及的关键信息（订单号、产品、时间等）

总结：
```

### 使用方式

```bash
# 交互模式中
[user001] 请输入用户反馈: /summarize

# 查看所有可用命令
[user001] 请输入用户反馈: commands
```

## Skill（技能）

### 什么是 Skill？

Skill 是注册为 LangChain Tool 的能力扩展，由 Agent 根据任务需求自主决策调用。

### 使用场景

- 解决方案推荐
- 升级检查
- 风险评估
- 智能建议

### 创建 Skill

1. 在 `skills/` 目录创建 `.md` 文件
2. 定义 YAML frontmatter（必须包含 `category: skill`）
3. 编写 Prompt 模板

### 模板格式

```markdown
---
name: 技能名称（英文）
description: 技能描述（会作为 Tool 的 description）
category: skill
inputs:
  - 参数1
  - 参数2
---

# Prompt 标题

这里是 Prompt 内容，使用 {参数1} 和 {参数2} 占位符。
```

### 示例：解决方案推荐技能

文件：`skills/suggest_solution.md`

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

根据用户反馈和知识库，推荐最合适的解决方案。

用户反馈：{feedback}
反馈分类：{category}

相关知识：
{knowledge}

请推荐：
1. 最佳解决方案（具体步骤）
2. 备选方案
3. 预计解决时间
4. 需要用户配合的事项

推荐方案：
```

### 使用方式

Skill 由 Agent 自动调用，无需用户手动触发。Agent 会根据任务需求决定是否调用某个 Skill。

```bash
# 查看所有可用技能
[user001] 请输入用户反馈: skills
```

## 工作原理

### Command 工作流程

```
用户输入 /summarize
    ↓
CommandManager.execute_command()
    ↓
加载 commands/summarize.md
    ↓
解析 YAML frontmatter
    ↓
提取 prompt 模板
    ↓
填充输入参数 {feedback}
    ↓
调用 LLM 执行
    ↓
返回结果
```

### Skill 工作流程

```
系统启动
    ↓
SkillManager.register_skills_as_tools()
    ↓
扫描 skills/ 目录
    ↓
为每个 Skill 创建 @tool 装饰的函数
    ↓
注册到 Agent 的工具列表
    ↓
Agent 处理任务时自主决策调用
    ↓
Skill Tool 执行并返回结果
```

## 核心组件

### TemplateLoader

负责加载和解析 Markdown 模板。

```python
template = TemplateLoader.load_template("commands/summarize.md")
# 返回:
# {
#     'name': 'summarize',
#     'description': '总结用户反馈的核心问题',
#     'trigger': '/summarize',
#     'inputs': ['feedback'],
#     'prompt': '# 反馈总结\n\n...'
# }
```

### CommandManager

管理用户命令。

```python
command_manager = CommandManager()

# 列出所有命令
commands = command_manager.list_commands()

# 执行命令
result = command_manager.execute_command(
    "summarize",
    llm=llm,
    feedback="我的订单还没发货"
)
```

### SkillManager

管理 Agent 技能。

```python
skill_manager = SkillManager(llm=llm)

# 注册技能为工具
tools = skill_manager.register_skills_as_tools()

# 列出所有技能
skills = skill_manager.list_skills()

# 获取工具列表（供 Agent 使用）
agent_tools = skill_manager.get_tools()
```

## 最佳实践

### Command 设计建议

1. **单一职责**：每个命令只做一件事
2. **清晰命名**：使用直观的触发词，如 `/summarize`、`/analyze`
3. **参数简洁**：尽量减少必需参数
4. **输出格式化**：使用结构化输出（列表、表格等）

### Skill 设计建议

1. **明确描述**：description 要清晰说明技能用途，帮助 Agent 决策
2. **合理参数**：只要求必需的输入参数
3. **可组合性**：设计可与其他工具组合使用的技能
4. **错误处理**：在 Prompt 中说明异常情况的处理方式

### Prompt 编写技巧

1. **结构清晰**：使用标题、列表、分隔符
2. **明确指令**：告诉 LLM 具体要做什么
3. **示例引导**：提供输出格式示例
4. **约束条件**：说明字数限制、格式要求等

## 示例集合

### Command 示例

#### 1. 趋势分析

```markdown
---
name: analyze_trend
description: 分析用户反馈趋势
trigger: /trend
inputs:
  - feedbacks
  - time_range
---

# 反馈趋势分析

分析以下时间段内的用户反馈趋势：

时间范围：{time_range}

反馈列表：
{feedbacks}

请分析：
1. 主要问题类型分布
2. 情绪变化趋势
3. 高频关键词
4. 需要重点关注的问题

分析结果：
```

#### 2. 报告生成

```markdown
---
name: generate_report
description: 生成反馈处理报告
trigger: /report
inputs:
  - user_id
  - date_range
---

# 反馈处理报告

为用户 {user_id} 生成 {date_range} 的反馈处理报告。

请包含：
1. 反馈总数
2. 分类统计
3. 处理情况
4. 转人工比例
5. 主要问题总结

报告：
```

### Skill 示例

#### 1. 升级检查

```markdown
---
name: escalate_check
description: 检查反馈是否需要升级处理
category: skill
inputs:
  - feedback
  - category
  - sentiment
  - user_history
---

# 升级检查

判断该反馈是否需要升级到更高级别处理。

用户反馈：{feedback}
分类：{category}
情绪：{sentiment}
用户历史：{user_history}

请判断：
1. 是否需要升级（是/否）
2. 升级原因
3. 建议升级级别（普通/紧急/特急）
4. 需要通知的部门

判断结果：
```

#### 2. 风险评估

```markdown
---
name: risk_assessment
description: 评估反馈的风险等级
category: skill
inputs:
  - feedback
  - category
  - sentiment
---

# 风险评估

评估该反馈可能带来的风险。

用户反馈：{feedback}
分类：{category}
情绪：{sentiment}

请评估：
1. 风险等级（低/中/高）
2. 潜在影响
3. 建议措施
4. 处理时限

评估结果：
```

## 常见问题

**Q: Command 和 Skill 有什么区别？**

A: Command 由用户主动调用（`/命令名`），Skill 由 Agent 自主决策调用。Command 适合快捷操作，Skill 适合扩展 Agent 能力。

**Q: 如何调试模板？**

A: 可以直接修改 `.md` 文件，重启系统后生效。建议先用简单的 Prompt 测试，再逐步完善。

**Q: 参数如何传递？**

A: Command 的参数需要在代码中指定，Skill 的参数由 Agent 自动填充。

**Q: 可以使用中文命名吗？**

A: `name` 字段建议使用英文，`description` 和 `trigger` 可以使用中文。

**Q: 如何删除命令或技能？**

A: 直接删除对应的 `.md` 文件，重启系统即可。

## 扩展建议

1. **添加更多命令**：根据业务需求创建专用命令
2. **丰富技能库**：为不同场景设计专门的技能
3. **模板复用**：提取通用的 Prompt 片段
4. **版本管理**：使用 Git 管理模板变更
5. **性能优化**：缓存常用模板，减少文件读取
