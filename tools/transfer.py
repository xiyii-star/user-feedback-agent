from langchain.tools import tool

@tool
def transfer_human(reason: str, priority: str = "normal") -> str:
    """
    将反馈转接给人工客服处理。

    参数:
        reason: 转接原因
        priority: 优先级 (low/normal/high/urgent)

    返回:
        转接结果确认信息
    """
    priority_map = {
        "low": "低",
        "normal": "普通",
        "high": "高",
        "urgent": "紧急"
    }

    priority_cn = priority_map.get(priority, "普通")

    return f"已转接人工客服 | 原因: {reason} | 优先级: {priority_cn} | 状态: 等待处理"
