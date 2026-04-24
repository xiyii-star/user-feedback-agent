from langchain.tools import tool

@tool
def sentiment_analyze(feedback: str) -> str:
    """
    分析用户反馈的情绪状态。

    参数:
        feedback: 用户反馈内容

    返回:
        情绪状态：正常/不满/愤怒
    """
    feedback_lower = feedback.lower()

    # 愤怒情绪检测
    angry_keywords = ["太离谱", "废物", "垃圾", "傻逼", "气死", "受够了", "!!!", "？？？"]
    angry_count = sum(1 for keyword in angry_keywords if keyword in feedback_lower)

    if angry_count >= 2 or "!" * 3 in feedback or "？" * 3 in feedback:
        return "愤怒"

    # 不满情绪检测
    dissatisfied_keywords = ["不满意", "失望", "差", "烂", "没人理", "催了", "还没", "怎么回事"]
    if any(keyword in feedback_lower for keyword in dissatisfied_keywords) or angry_count == 1:
        return "不满"

    # 默认为正常
    return "正常"
