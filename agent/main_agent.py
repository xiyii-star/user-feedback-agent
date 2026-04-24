from langchain_openai import ChatOpenAI
from tools import (
    feedback_classify,
    sentiment_analyze,
    extract_entities,
    rag_search,
    transfer_human,
    save_report
)
from agent.sub_agents import UnderstandingAgent, ReplyAgent, ExecutionAgent
from agent.memory import UserMemory
import json
from typing import Dict

class MainAgent:
    """主Agent：负责整体编排和决策"""

    def __init__(self, api_key: str, base_url: str = None, model: str = "gpt-4"):
        # 初始化LLM
        self.llm = ChatOpenAI(
            api_key=api_key,
            base_url=base_url,
            model=model,
            temperature=0.7
        )

        # 初始化子代理
        self.understanding_agent = UnderstandingAgent(self.llm)
        self.reply_agent = ReplyAgent(self.llm)
        self.execution_agent = ExecutionAgent(self.llm)

        # 初始化记忆
        self.memory = UserMemory()

    def process_feedback(self, feedback: str, user_id: str = "default") -> Dict:
        """
        处理用户反馈的主流程

        参数:
            feedback: 用户反馈内容
            user_id: 用户ID

        返回:
            处理结果字典
        """
        # 加载用户历史
        user_context = self.memory.get_user_context(user_id)

        # 步骤1: 理解阶段 - 调用工具获取基础信息
        print("\n=== 步骤1: 理解用户反馈 ===")
        category = feedback_classify.invoke({"feedback": feedback})
        sentiment = sentiment_analyze.invoke({"feedback": feedback})
        entities = extract_entities.invoke({"feedback": feedback})

        print(f"分类: {category}")
        print(f"情绪: {sentiment}")
        print(f"抽取信息: {entities}")

        # 步骤2: 检索知识库
        print("\n=== 步骤2: 检索知识库 ===")
        knowledge = rag_search.invoke({"query": feedback, "top_k": 3})
        print(f"检索结果: {knowledge[:200]}...")

        # 步骤3: 生成回复
        print("\n=== 步骤3: 生成回复 ===")
        reply = self.reply_agent.generate_reply(
            feedback=feedback,
            category=category,
            sentiment=sentiment,
            knowledge=knowledge
        )
        print(f"回复内容: {reply}")

        # 步骤4: 判断是否转人工
        print("\n=== 步骤4: 判断处理动作 ===")
        should_transfer, reason, priority = self.execution_agent.should_transfer(
            category, sentiment, user_context
        )

        transfer_result = ""
        if should_transfer:
            transfer_result = transfer_human.invoke({"reason": reason, "priority": priority})
            print(f"转接结果: {transfer_result}")
        else:
            print("无需转人工，自动处理")

        action = self.execution_agent.generate_action(category, sentiment)

        # 步骤5: 生成处理报告
        print("\n=== 步骤5: 生成处理报告 ===")
        result = {
            "用户反馈": feedback,
            "分类": category,
            "情绪": sentiment,
            "抽取信息": entities,
            "检索结果": knowledge[:300] + "..." if len(knowledge) > 300 else knowledge,
            "处理动作": action,
            "是否转人工": should_transfer,
            "转接信息": transfer_result if should_transfer else "无",
            "回复内容": reply,
            "用户ID": user_id
        }

        report_result = save_report.invoke({"report_data": json.dumps(result, ensure_ascii=False)})
        result["处理报告"] = report_result

        # 更新记忆
        self.memory.add_session_memory(feedback, result)
        self.memory.update_user_history(user_id, category, should_transfer)

        return result
