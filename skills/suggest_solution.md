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
