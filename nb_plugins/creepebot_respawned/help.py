import re

from lib.chat.context import Context
from lib.chat.html_renderer import render
from lib.html_files.help import generate_help_html
from lib.rule_registry import register, get_registry

from lib.chat.rules import Command


@register
class Help(Command):
    def __init__(self):
        super().__init__('hlp', '帮助', '查看帮助, 也可根据关键词进行搜索', '/help [参数] <关键词>', 0, True)

    def check(self, context: Context) -> bool:
        return re.match(r'/help.*', context.get_message())

    async def handle(self, context: Context) -> bool:
        message = context.get_message()

        # 无参情况
        if message == '/help':
            await context.send_message(await render(generate_help_html(get_registry())))

        # 有参数
        elif re.match(r'/help -[nud]* .+', message):
            arg = re.search(r'/help -([nud]*) .+', message).group(1)
            key = re.search(r'/help -[nud]* (.+)', message).group(1)
            found = []

            for rule in get_registry():
                if 'n' in arg:
                    if key in rule.name: found.append(rule)
                if 'u' in arg:
                    if key in rule.usage: found.append(rule)
                if 'd' in arg:
                    if key in rule.desc: found.append(rule)

            await context.send_message(await render(generate_help_html(found)))

        # 无参数
        elif re.match(r'/help .+', message):
            key = re.search(r'/help (.+)', message).group(1)
            found = []

            for rule in get_registry():
                if key in rule.name: found.append(rule)

            await context.send_message(await render(generate_help_html(found)))

        # 其他情况
        else:
            await context.send_message('未知指令结构. 使用/help -u help了解详情')

        return False


