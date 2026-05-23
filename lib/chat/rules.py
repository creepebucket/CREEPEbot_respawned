from lib.chat.rule import Rule


class Command(Rule):

    def __init__(self, id: str, name: str, desc: str, usage: str, priority: int = 0, bypass_enable_check: bool = False):
        """
        构造函数, 这些参数将用于自动填充/help命令, 支持Markdown
        :param name: 指令的名称
        :param desc: 指令简介
        :param priority: 优先级, 值越高越优先
        """
        self.id = id
        self.name = name
        self.desc = desc
        self.usage = usage
        self.priority = priority
        self.bypass_enable_check = bypass_enable_check