from langchain.tools import tool
import re
from typing import Dict, Any

@tool
def extract_entities(feedback: str) -> str:
    """
    从用户反馈中抽取关键信息。

    参数:
        feedback: 用户反馈内容

    返回:
        JSON格式的抽取结果，包含订单号、设备信息、联系方式、问题摘要等
    """
    entities = {}

    # 订单号提取 (6-20位数字)
    order_pattern = r'订单[号]?\s*[：:]\s*(\d{6,20})|订单\s*(\d{6,20})'
    order_match = re.search(order_pattern, feedback)
    if order_match:
        entities["订单号"] = order_match.group(1) or order_match.group(2)

    # 设备信息提取
    device_patterns = [
        r'(iPhone\s*\d+\s*(?:Pro|Max|Plus)?)',
        r'(Android|安卓)',
        r'(华为|小米|OPPO|vivo|三星)\s*[\w\s]*',
        r'iOS\s*(\d+)',
        r'Android\s*(\d+)'
    ]
    for pattern in device_patterns:
        match = re.search(pattern, feedback, re.IGNORECASE)
        if match:
            entities["设备"] = match.group(0)
            break

    # 联系方式提取
    phone_pattern = r'1[3-9]\d{9}'
    phone_match = re.search(phone_pattern, feedback)
    if phone_match:
        entities["联系方式"] = phone_match.group(0)

    wechat_pattern = r'微信[：:]\s*([\w-]+)|加我微信\s*([\w-]+)'
    wechat_match = re.search(wechat_pattern, feedback)
    if wechat_match:
        entities["联系方式"] = f"微信: {wechat_match.group(1) or wechat_match.group(2)}"

    # 问题摘要（简单提取前50字）
    summary = feedback[:50] + "..." if len(feedback) > 50 else feedback
    entities["问题摘要"] = summary

    return str(entities)
