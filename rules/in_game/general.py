from lib.chat.context import Context
from lib.chat.rule import Rule
from lib.rule_registry import register


@register
class InGameHelp(Rule):
    def __init__(self):
        super().__init__('游戏内帮助')

    def check(self, context: Context) -> bool:
        return context.chat_session.is_mc_chat() and context.get_message().startswith('!!bot')

    async def handle(self, context: Context) -> bool:
        await context.send_message('--- 欢迎使用 CREEPEbot respawned ---')