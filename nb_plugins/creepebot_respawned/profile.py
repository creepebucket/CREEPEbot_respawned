import re

from lib.chat.context import Context
from lib.chat.html_renderer import render
from lib.database.config import PersonalConfig
from lib.html_files.profile import get_profile_html
from lib.rule_registry import register

from lib.chat.rules import Command


@register
class Me(Command):

    def __init__(self):
        super().__init__('prf', '个人信息', '显示某人的权限等级和标签信息(默认显示自己的)', '/profile [qid/at消息]', bypass_enable_check=True)

    def check(self, context: Context) -> bool:
        return context.get_message().startswith('/profile')

    async def handle(self, context: Context) -> bool:
        message = context.get_message()

        if context.chat_session.is_private_chat():
            await context.send_message('/profile 在私聊中不可用')

            return False

        if re.match(r'/profile \[at:[0-9]+]', message):
            query = PersonalConfig(int(re.search(r'/profile \[at:([0-9]+)', message).group(1)))

            await context.send_message(await render(get_profile_html(
                query.qid,
                context.chat_session.session_id,
                await context.chat_session.get_permission(query.qid),
                query.get_role(),
                query.get_tags()
            )))

            return False

        await context.send_message(await render(get_profile_html(
                    context.sender.qid,
                    context.chat_session.session_id,
              await context.chat_session.get_permission(context.sender.qid),
                    context.sender.get_role(),
                    context.sender.get_tags()
        )))
        return False

