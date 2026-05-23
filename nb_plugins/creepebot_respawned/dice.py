import html
import random
import re

from lib.chat.context import Context
from lib.chat.html_renderer import render
from lib.html_files.dice import get_roll_html
from lib.rule_registry import register
from lib.chat.rules import Command


@register
class Dice(Command):
    def __init__(self):
        super().__init__('rll', '骰子', '投掷骰子并输出统计卡片（支持 NdM / dM / N 等写法）',
                         '/roll [N]dM | /roll N | /roll')

    def check(self, context: Context) -> bool:
        return context.get_message().startswith('/roll')

    async def handle(self, context: Context) -> bool:
        message = context.get_message().strip()

        tail = message[len('/roll'):].strip() if message.startswith('/roll') else ''

        if not tail:
            count, sides, info = 1, 6, '1d6'
        elif re.fullmatch(r'[0-9]+', tail):
            count = int(tail)
            sides = 6
            info = f'{count}d6'
        else:
            m = re.fullmatch(r'(?:(?P<count>[0-9]+))?d(?P<sides>[0-9]+)', tail, flags=re.IGNORECASE)
            if not m:
                await context.send_message('指令格式错误! 使用/help -u /roll查看详情')
                return False

            count = int(m.group('count') or '1')
            sides = int(m.group('sides'))
            info = f'{count}d{sides}'

        if count <= 0 or sides <= 1:
            await context.send_message('骰子参数非法：数量必须大于0，面数必须大于1')
            return False

        if count > 50:
            await context.send_message('一次最多投掷 50 个骰子')
            return False

        if sides > 10_000:
            await context.send_message('骰子面数过大（最大 10000）')
            return False

        values = [random.randint(1, sides) for _ in range(count)]
        safe_info = html.escape(info)

        await context.send_message(await render(get_roll_html(values, safe_info)))
        return False
