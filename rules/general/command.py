import re

from lib.chat.context import Context
from lib.chat.html_renderer import render
from lib.html_files.command import get_command_list_html
from lib.rule_registry import register, get_registry

from lib.chat.rules import QqCommand as CommandBase

@register
class Command(CommandBase):

    def __init__(self):
        super().__init__('cmd', '启用指令', '为某个id启用指令, 仅在当前会话生效 -e: 启用 -d: 禁用, all表示全部指令', '/cmd <-e/-d> <id0> [id1] [id2] [id3] [id4]...', bypass_enable_check=True)

    def check(self, context: Context) -> bool:
        return context.get_message().startswith('/cmd ')

    async def handle(self, context: Context) -> bool:

        message = context.get_message()

        if not re.match(r'/cmd -[ed] .*', message):
            await context.send_message('指令格式错误! 使用/help -u /cmd查看详情')
            return False

        if await context.chat_session.get_permission(context.sender.name) < 1:
            await context.send_message('/cmd 需要至少1级权限')
            return False

        args = message.split(' ')
        ids = []

        for i in args[2:]:
            if not re.match(r'^[a-z]{3}$', i) and i != 'all':
                await context.send_message(f'提供的指令id {i} 非法, 仅支持3位小写字母或all')
                return False

            ids.append(i)

        if 'all' in ids:
            ids = [i.id for i in get_registry() if hasattr(i, 'id')]
        else:
            ids = list(dict.fromkeys(ids))

        for i in ids:
            context.chat_session.set_rule_status(i, args[1] == '-e')

        await context.send_message(f'已{'启用' if args[1] == '-e' else '禁用'} {len(ids)} 条指令')

        return False


@register
class Commands(CommandBase):

    def __init__(self):
        super().__init__('cms', '指令列表', '查看当前会话下各指令启用状态', '/cmds', bypass_enable_check=True)

    def check(self, context: Context) -> bool:
        return context.get_message() == '/cmds'

    async def handle(self, context: Context) -> bool:

        all_commands = [i for i in get_registry() if hasattr(i, 'id')]
        enabled_commands = [i for i in all_commands if i.bypass_enable_check or context.chat_session.is_rule_enabled(i.id)]

        await context.send_message(await render(get_command_list_html(enabled_commands, all_commands)))
        return False

