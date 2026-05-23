from abc import ABC, abstractmethod

from lib.chat.context import Context


class Rule(ABC):
    """
    定义了一条回复规则
    请继承我创建自己的回复规则
    """

    def __init__(self, name, priority: int = 0):
        self.name = name
        self.priority = priority

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
