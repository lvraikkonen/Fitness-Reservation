from typing import Dict, Any
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape


class TemplateManager:
    def __init__(self):
        current_file = Path(__file__)
        template_dir = current_file.parent.parent / 'templates'
        self.env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=select_autoescape(['html', 'xml'])
        )

    def render_template(self, template_name: str, context: Dict[str, Any]) -> str:
        """
        渲染指定的模板，填充上下文数据
        """
        template = self.env.get_template(f"email/{template_name}.html")
        return template.render(**context)


# 创建一个全局的TemplateManager实例
template_manager = TemplateManager()


def get_notification_template(template_name: str, context: Dict[str, Any]) -> str:
    return template_manager.render_template(template_name, context)
