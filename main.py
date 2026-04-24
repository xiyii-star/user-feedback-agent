#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import argparse
import json
from dotenv import load_dotenv
from agent.main_agent import MainAgent

def print_result(result: dict):
    """格式化打印处理结果"""
    print("\n" + "="*60)
    print("处理结果")
    print("="*60)

    print(f"\n【用户反馈】\n{result['用户反馈']}")
    print(f"\n【分类】{result['分类']}")
    print(f"【情绪】{result['情绪']}")
    print(f"\n【抽取信息】\n{result['抽取信息']}")
    print(f"\n【处理动作】{result['处理动作']}")
    print(f"【是否转人工】{'是' if result['是否转人工'] else '否'}")

    if result['是否转人工']:
        print(f"【转接信息】{result['转接信息']}")

    print(f"\n【回复内容】\n{result['回复内容']}")
    print(f"\n【处理报告】{result['处理报告']}")
    print("\n" + "="*60)

def interactive_mode(agent: MainAgent):
    """交互模式"""
    print("\n欢迎使用用户反馈智能处理系统")
    print("输入 'quit' 或 'exit' 退出")
    print("输入 'history' 查看会话记忆")
    print("输入 'commands' 查看可用命令")
    print("输入 'skills' 查看可用技能")
    print("输入 '/命令名' 执行命令")
    print("-" * 60)

    user_id = input("\n请输入用户ID（默认: default）: ").strip() or "default"

    while True:
        feedback = input(f"\n[{user_id}] 请输入用户反馈: ").strip()

        if feedback.lower() in ['quit', 'exit']:
            print("\n感谢使用，再见！")
            break

        if feedback.lower() == 'history':
            history = agent.memory.get_session_memory()
            print("\n=== 会话记忆 ===")
            for i, mem in enumerate(history, 1):
                print(f"{i}. {mem['feedback'][:50]}... (分类: {mem['result'].get('分类', '未知')})")
            continue

        if feedback.lower() == 'commands':
            print("\n=== 可用命令 ===")
            for cmd in agent.list_commands():
                print(f"  {cmd}")
            continue

        if feedback.lower() == 'skills':
            print("\n=== 可用技能 ===")
            for skill in agent.list_skills():
                print(f"  {skill}")
            continue

        # 处理命令调用
        if feedback.startswith('/'):
            command_parts = feedback[1:].split()
            command_name = command_parts[0]

            # 获取命令参数
            print(f"\n执行命令: {command_name}")
            # 简单示例：从最近的反馈获取参数
            recent_feedback = ""
            history = agent.memory.get_session_memory()
            if history:
                recent_feedback = history[-1]['feedback']

            try:
                result = agent.execute_command(command_name, feedback=recent_feedback)
                print(f"\n命令结果:\n{result}")
            except Exception as e:
                print(f"\n命令执行失败: {str(e)}")
            continue

        if not feedback:
            print("反馈内容不能为空")
            continue

        try:
            result = agent.process_feedback(feedback, user_id)
            print_result(result)
        except Exception as e:
            print(f"\n处理失败: {str(e)}")

def main():
    # 加载环境变量
    load_dotenv()

    api_key = os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("OPENAI_API_BASE")
    model = os.getenv("MODEL_NAME", "gpt-4")

    if not api_key:
        print("错误: 未找到 OPENAI_API_KEY")
        print("请创建 .env 文件并配置 API Key")
        sys.exit(1)

    # 解析命令行参数
    parser = argparse.ArgumentParser(description="用户反馈智能处理系统")
    parser.add_argument("--feedback", "-f", type=str, help="直接处理单条反馈")
    parser.add_argument("--user-id", "-u", type=str, default="default", help="用户ID")
    parser.add_argument("--batch", "-b", type=str, help="批量处理文件路径（JSON格式）")

    args = parser.parse_args()

    # 初始化Agent
    print("正在初始化系统...")
    agent = MainAgent(api_key=api_key, base_url=base_url, model=model)
    print("系统初始化完成\n")

    # 单条反馈处理
    if args.feedback:
        try:
            result = agent.process_feedback(args.feedback, args.user_id)
            print_result(result)
        except Exception as e:
            print(f"处理失败: {str(e)}")
        return

    # 批量处理
    if args.batch:
        if not os.path.exists(args.batch):
            print(f"错误: 文件不存在 {args.batch}")
            sys.exit(1)

        with open(args.batch, 'r', encoding='utf-8') as f:
            feedbacks = json.load(f)

        for i, item in enumerate(feedbacks, 1):
            feedback = item.get("feedback", "")
            user_id = item.get("user_id", "default")

            print(f"\n处理第 {i}/{len(feedbacks)} 条反馈...")
            try:
                result = agent.process_feedback(feedback, user_id)
                print_result(result)
            except Exception as e:
                print(f"处理失败: {str(e)}")

        return

    # 交互模式
    interactive_mode(agent)

if __name__ == "__main__":
    main()
