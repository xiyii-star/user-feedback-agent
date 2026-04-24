from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from typing import Dict

class UnderstandingAgent:
    """理解子代理：负责分类、情绪、信息抽取"""

    def __init__(self, llm: ChatOpenAI):
        self.llm = llm

    def process(self, feedback: str, tools_result: Dict) -> Dict:
        """处理理解任务"""
        return {
            "分类": tools_result.get("classify", "未知"),
            "情绪": tools_result.get("sentiment", "未知"),
            "抽取信息": tools_result.get("entities", {})
        }


class ReplyAgent:
    """回复子代理：根据RAG结果生成回复"""

    def __init__(self, llm: ChatOpenAI):
        self.llm = llm
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """你是一个专业的客服助手。根据用户反馈和检索到的知识库内容，生成合适的回复。

要求：
1. 语气友好、专业
2. 针对用户问题给出具体解决方案
3. 如果是投诉，先道歉再解决
4. 如果是建议，表示感谢并说明处理方式
5. 回复简洁明了，不超过150字

用户反馈分类：{category}
用户情绪：{sentiment}
检索到的知识：
{knowledge}
"""),
            ("user", "用户反馈：{feedback}")
        ])

    def generate_reply(self, feedback: str, category: str, sentiment: str, knowledge: str) -> str:
        """生成回复内容"""
        try:
            chain = self.prompt | self.llm
            response = chain.invoke({
                "feedback": feedback,
                "category": category,
                "sentiment": sentiment,
                "knowledge": knowledge
            })
            return response.content
        except Exception as e:
            return f"回复生成失败: {str(e)}"


class ExecutionAgent:
    """执行子代理：判断转人工、生成报告"""

    def __init__(self, llm: ChatOpenAI):
        self.llm = llm

    def should_transfer(self, category: str, sentiment: str, user_context: str) -> tuple[bool, str, str]:
        """
        判断是否需要转人工

        返回: (是否转接, 转接原因, 优先级)
        """
        # 辱骂和广告直接拒绝，不转人工
        if category in ["辱骂", "广告"]:
            return False, "违规内容，不予处理", "low"

        # 愤怒情绪 + 投诉 = 高优先级转人工
        if sentiment == "愤怒" and category == "投诉":
            return True, "用户情绪激烈的投诉", "urgent"

        # 投诉类 + 不满情绪 = 普通优先级转人工
        if category == "投诉" and sentiment == "不满":
            return True, "用户投诉需人工处理", "high"

        # 重复投诉用户
        if "是否重复投诉用户: 是" in user_context:
            return True, "重复投诉用户，需人工跟进", "high"

        # Bug类问题
        if category == "Bug":
            return True, "技术问题需人工确认", "normal"

        # 其他情况不转人工
        return False, "", "low"

    def generate_action(self, category: str, sentiment: str) -> str:
        """生成处理动作"""
        if category == "辱骂":
            return "警告并记录违规行为"
        elif category == "广告":
            return "删除内容并警告"
        elif category == "投诉":
            return "转人工处理"
        elif category == "Bug":
            return "转技术团队"
        elif category == "建议":
            return "记录并转产品团队"
        else:
            return "自动回复"
