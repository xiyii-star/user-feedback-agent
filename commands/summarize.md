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
