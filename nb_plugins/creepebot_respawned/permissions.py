import re
from selectors import SelectSelector

from lib import logger
from lib.chat.context import Context
from lib.database.config import PersonalConfig
from lib.rule_registry import register

from .rules import Command


@register
class SetPermission(Command):

    def __init__(self):
        super().__init__('prm', '设置权限', '设置某人的权限 (可以使用qid或者at), 权限范围0-10', '/perm <qid/at消息> <权限>', bypass_enable_check=True)

    def check(self, context: Context) -> bool:
        return context.get_message().startswith('/perm')

    async def handle(self, context: Context) -> bool:
        message = context.get_message()

        if not re.match(r'/perm (\[at:[0-9]+]|[0-9]+) [0-9]+', message):
            await context.send_message('指令格式错误! 使用/help -u /perm查看详情')
            return False

        elif context.chat_session.is_private_chat():
            await context.send_message('/perm 在私聊中不可用')
            return False

        qid = int(
            re.search(r'/perm \[at:([0-9]+)] [0-9]+', message).group(1)
            if re.match(r'/perm \[at:([0-9]+)] [0-9]+', message) else
            re.search(r'/perm ([0-9]+) [0-9]+', message).group(1)
        )

        logger.crit(context.get_message())

        perm = int(
            re.search(r'/perm (?:\[at:[0-9]+]|[0-9]+) ([0-9]+)', message).group(1)
        )

        sender_perm = await context.chat_session.get_permission(context.sender.qid)

        if sender_perm <= perm and context.sender.get_role() == 'USER':
            await context.send_message(f'错误: 您只能设置低于自己的权限等级的等级 ({sender_perm})')
            return False

        context.chat_session.set_permission(qid, perm)
        await context.send_message(f'已将 {qid} 的权限设为 {perm}')

        return False


@register
class Tag(Command):

    def __init__(self):
        super().__init__('tag', '设置标签', '设置某人的标签状态 -a: 增加, -d: 移除', '/tag <-a/d> <qid/at消息> <标签>', bypass_enable_check=True)

    def check(self, context: Context) -> bool:
        return context.get_message().startswith('/tag')

    async def handle(self, context: Context) -> bool:
        message = context.get_message()

        if not re.match(r'/tag -[ad] \[at:[0-9]+]|[0-9]+ .*', message):
            await context.send_message('指令格式错误! 使用/help -u /tag查看详情')
            return False

        if context.sender.get_role() == 'USER':
            await context.send_message(f'错误: 仅管理员可以使用此指令')
            return False

        args = message.split(' ')

        if args[2].startswith('[at:'):
            args[2] = args[2][4:-1]

        args[2] = int(args[2])

        if args[1] == '-a':
            PersonalConfig(args[2]).add_tag(args[3])
        if args[1] == '-d':
            PersonalConfig(args[2]).del_tag(args[3])

        await context.send_message(f'已为 {args[2]} {'添加' if args[1] == '-a' else '移除'}标签 {args[3]}')

        return False


@register
class Role(Command):

    def __init__(self):
        super().__init__('rol', '设置身份', '设置某人为用户/管理员', '/role <qid/at消息> <user/admin>', bypass_enable_check=True)

    def check(self, context: Context) -> bool:
        return context.get_message().startswith('/role')

    async def handle(self, context: Context) -> bool:
        message = context.get_message()

        if not re.match(r'/role \[at:[0-9]+]|[0-9]+ (user)|(admin)', message):
            await context.send_message('指令格式错误! 使用/help -u /tag查看详情')
            return False

        if context.sender.get_role() != 'SUPER_ADMIN':
            await context.send_message(f'错误: 仅超级管理员可以使用此指令')
            return False

        args = message.split(' ')

        if args[1].startswith('[at:'):
            args[1] = args[1][4:-1]

        args[1] = int(args[1])

        PersonalConfig(args[1]).set_role(args[2].upper())

        await context.send_message(f'已设置 {args[1]} 的身份为 {args[2]}')

        return False
