from langchain.tools import tool
import json
import os
from datetime import datetime

@tool
def save_report(report_data: str) -> str:
    """
    保存处理报告到本地文件。

    参数:
        report_data: JSON格式的报告数据

    返回:
        保存结果和文件路径
    """
    try:
        # 确保目录存在
        report_dir = "data/reports"
        os.makedirs(report_dir, exist_ok=True)

        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"report_{timestamp}.json"
        filepath = os.path.join(report_dir, filename)

        # 解析并格式化数据
        try:
            data = json.loads(report_data) if isinstance(report_data, str) else report_data
        except:
            data = {"raw_data": report_data}

        data["timestamp"] = datetime.now().isoformat()

        # 保存文件
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        return f"报告已保存至: {filepath}"

    except Exception as e:
        return f"保存失败: {str(e)}"
