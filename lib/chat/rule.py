from abc import ABC, abstractmethod

from lib.chat.context import Context


class Rule(ABC):
    """
    定义了一条回复规则
    请继承我创建自己的回复规则
    """

    def __init__(self, name: str, desc: str, usage: str, priority: int = 0, bypass_enable_check: bool = False):
        """
        构造函数, 这些参数将用于自动填充/help命令, 支持Markdown
        :param name: 指令的名称
        :param desc: 指令简介
        :param priority: 优先级, 值越高越优先
        """
        self.name = name
        self.desc = desc
        self.usage = usage
        self.priority = priority
        self.bypass_enable_check = bypass_enable_check

    @abstractmethod
    def check(self, context: Context) -> bool:
        """
        检查是否需要执行handle()
        :return: 是否需要执行
        """
        pass

    @abstractmethod
    async def handle(self, context: Context) -> bool:
        """
        具体处理消息, 已经检查完成
        :return: 是否阻断消息传播
        """
        pass
