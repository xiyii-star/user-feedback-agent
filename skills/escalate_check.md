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
