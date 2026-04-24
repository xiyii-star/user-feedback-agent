import json
import os
from datetime import datetime
from typing import Dict, List, Optional

class UserMemory:
    """用户记忆管理类"""

    def __init__(self, memory_dir: str = "data/memory"):
        self.memory_dir = memory_dir
        os.makedirs(memory_dir, exist_ok=True)
        self.session_memory: List[Dict] = []  # 会话记忆
        self.user_history: Dict = {}  # 用户历史摘要

    def add_session_memory(self, feedback: str, result: Dict):
        """添加会话记忆"""
        self.session_memory.append({
            "timestamp": datetime.now().isoformat(),
            "feedback": feedback,
            "result": result
        })

        # 只保留最近5条
        if len(self.session_memory) > 5:
            self.session_memory = self.session_memory[-5:]

    def get_session_memory(self) -> List[Dict]:
        """获取会话记忆"""
        return self.session_memory

    def load_user_history(self, user_id: str) -> Dict:
        """加载用户历史记忆"""
        filepath = os.path.join(self.memory_dir, f"user_{user_id}.json")

        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                self.user_history = json.load(f)
        else:
            self.user_history = {
                "user_id": user_id,
                "total_feedbacks": 0,
                "complaint_count": 0,
                "transferred_count": 0,
                "last_feedback_time": None,
                "is_repeat_complainer": False,
                "history_summary": []
            }

        return self.user_history

    def update_user_history(self, user_id: str, feedback_type: str, transferred: bool):
        """更新用户历史记忆"""
        if not self.user_history or self.user_history.get("user_id") != user_id:
            self.load_user_history(user_id)

        self.user_history["total_feedbacks"] += 1
        self.user_history["last_feedback_time"] = datetime.now().isoformat()

        if feedback_type == "投诉":
            self.user_history["complaint_count"] += 1

        if transferred:
            self.user_history["transferred_count"] += 1

        # 判断是否为重复投诉用户
        if self.user_history["complaint_count"] >= 3:
            self.user_history["is_repeat_complainer"] = True

        # 保存历史摘要（只保留最近10条）
        self.user_history["history_summary"].append({
            "time": datetime.now().isoformat(),
            "type": feedback_type,
            "transferred": transferred
        })

        if len(self.user_history["history_summary"]) > 10:
            self.user_history["history_summary"] = self.user_history["history_summary"][-10:]

        # 持久化
        self.save_user_history(user_id)

    def save_user_history(self, user_id: str):
        """保存用户历史记忆"""
        filepath = os.path.join(self.memory_dir, f"user_{user_id}.json")

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.user_history, f, ensure_ascii=False, indent=2)

    def get_user_context(self, user_id: str) -> str:
        """获取用户上下文信息（用于Agent决策）"""
        if not self.user_history or self.user_history.get("user_id") != user_id:
            self.load_user_history(user_id)

        context = f"""
用户历史信息：
- 总反馈次数: {self.user_history['total_feedbacks']}
- 投诉次数: {self.user_history['complaint_count']}
- 转人工次数: {self.user_history['transferred_count']}
- 是否重复投诉用户: {'是' if self.user_history['is_repeat_complainer'] else '否'}
"""

        if self.session_memory:
            context += "\n最近会话记录:\n"
            for mem in self.session_memory[-3:]:
                context += f"- {mem['feedback'][:50]}... (分类: {mem['result'].get('分类', '未知')})\n"

        return context
