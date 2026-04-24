import os
import yaml
from typing import Dict, List, Optional
from langchain.tools import tool
from langchain_openai import ChatOpenAI


class TemplateLoader:
    """加载和解析 Markdown 模板"""

    @staticmethod
    def load_template(file_path: str) -> Dict:
        """
        加载单个模板文件

        返回:
            {
                'name': str,
                'description': str,
                'trigger': str (可选),
                'category': str (可选),
                'inputs': List[str],
                'prompt': str
            }
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 分离 YAML frontmatter 和 prompt
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                frontmatter = yaml.safe_load(parts[1])
                prompt = parts[2].strip()
            else:
                raise ValueError(f"Invalid template format in {file_path}")
        else:
            raise ValueError(f"Template must start with YAML frontmatter in {file_path}")

        return {
            'name': frontmatter.get('name'),
            'description': frontmatter.get('description'),
            'trigger': frontmatter.get('trigger'),
            'category': frontmatter.get('category'),
            'inputs': frontmatter.get('inputs', []),
            'prompt': prompt
        }

    @staticmethod
    def load_all_templates(directory: str) -> Dict[str, Dict]:
        """加载目录下所有模板"""
        templates = {}

        if not os.path.exists(directory):
            return templates

        for filename in os.listdir(directory):
            if filename.endswith('.md'):
                file_path = os.path.join(directory, filename)
                try:
                    template = TemplateLoader.load_template(file_path)
                    templates[template['name']] = template
                except Exception as e:
                    print(f"Error loading template {filename}: {e}")

        return templates


class CommandManager:
    """管理用户命令"""

    def __init__(self, commands_dir: str = "commands"):
        self.commands_dir = commands_dir
        self.commands = TemplateLoader.load_all_templates(commands_dir)

    def list_commands(self) -> List[str]:
        """列出所有可用命令"""
        return [f"{cmd['trigger']} - {cmd['description']}"
                for cmd in self.commands.values() if cmd.get('trigger')]

    def execute_command(self, command_name: str, llm: ChatOpenAI, **kwargs) -> str:
        """
        执行命令

        参数:
            command_name: 命令名称（不含 /）
            llm: LLM 实例
            **kwargs: 命令所需的输入参数
        """
        if command_name not in self.commands:
            return f"命令 '{command_name}' 不存在"

        template = self.commands[command_name]

        # 检查必需参数
        missing_inputs = [inp for inp in template['inputs'] if inp not in kwargs]
        if missing_inputs:
            return f"缺少必需参数: {', '.join(missing_inputs)}"

        # 填充 prompt
        try:
            prompt = template['prompt'].format(**kwargs)
        except KeyError as e:
            return f"参数错误: {e}"

        # 调用 LLM
        response = llm.invoke(prompt)
        return response.content


class SkillManager:
    """管理 Agent 技能"""

    def __init__(self, skills_dir: str = "skills", llm: ChatOpenAI = None):
        self.skills_dir = skills_dir
        self.skills = TemplateLoader.load_all_templates(skills_dir)
        self.llm = llm
        self._registered_tools = []

    def register_skills_as_tools(self) -> List:
        """将所有技能注册为 LangChain Tools"""
        tools = []

        for skill_name, skill_template in self.skills.items():
            # 动态创建 tool 函数
            tool_func = self._create_tool_function(skill_name, skill_template)
            tools.append(tool_func)

        self._registered_tools = tools
        return tools

    def _create_tool_function(self, skill_name: str, skill_template: Dict):
        """为每个技能创建一个 tool 函数"""

        inputs = skill_template['inputs']
        description = skill_template['description']
        prompt_template = skill_template['prompt']
        llm = self.llm

        # 动态创建函数
        def skill_tool(**kwargs) -> str:
            """动态生成的技能工具"""
            # 检查必需参数
            missing = [inp for inp in inputs if inp not in kwargs]
            if missing:
                return f"缺少参数: {', '.join(missing)}"

            # 填充 prompt
            try:
                prompt = prompt_template.format(**kwargs)
            except KeyError as e:
                return f"参数错误: {e}"

            # 调用 LLM
            if llm:
                response = llm.invoke(prompt)
                return response.content
            else:
                return "LLM 未初始化"

        # 设置函数名称和文档
        skill_tool.__name__ = skill_name
        skill_tool.__doc__ = description

        # 使用 @tool 装饰器
        return tool(skill_tool)

    def get_tools(self) -> List:
        """获取已注册的工具列表"""
        if not self._registered_tools:
            self.register_skills_as_tools()
        return self._registered_tools

    def list_skills(self) -> List[str]:
        """列出所有可用技能"""
        return [f"{name} - {skill['description']}"
                for name, skill in self.skills.items()]
