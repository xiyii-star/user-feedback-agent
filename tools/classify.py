from langchain.tools import tool
from typing import Literal

@tool
def feedback_classify(feedback: str) -> str:
    """
    对用户反馈进行分类。

    参数:
        feedback: 用户反馈内容

    返回:
        分类结果：咨询/投诉/建议/Bug/辱骂/广告
    """
    feedback_lower = feedback.lower()

    # 辱骂检测
    abuse_keywords = ["废物", "垃圾", "傻逼", "sb", "nmsl", "草泥马", "fuck", "shit"]
    if any(keyword in feedback_lower for keyword in abuse_keywords):
        return "辱骂"

    # 广告检测
    ad_keywords = ["加微信", "加qq", "便宜出售", "代购", "刷单", "兼职", "赚钱"]
    if any(keyword in feedback_lower for keyword in ad_keywords):
        return "广告"

    # Bug 检测
    bug_keywords = ["闪退", "崩溃", "打不开", "卡死", "黑屏", "白屏", "报错", "bug"]
    if any(keyword in feedback_lower for keyword in bug_keywords):
        return "Bug"

    # 投诉检测
    complaint_keywords = ["投诉", "太离谱", "没人理", "不满意", "差评", "退款", "赔偿"]
    if any(keyword in feedback_lower for keyword in complaint_keywords):
        return "投诉"

    # 建议检测
    suggestion_keywords = ["建议", "希望", "能不能", "最好", "应该", "增加", "改进"]
    if any(keyword in feedback_lower for keyword in suggestion_keywords):
        return "建议"

    # 默认为咨询
    return "咨询"
