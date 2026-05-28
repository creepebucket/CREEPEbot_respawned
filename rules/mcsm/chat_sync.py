import re
from typing import List, Dict

import nonebot

from lib.chat.context import Context
from lib.chat.rule import Rule
from lib.chat.rules import QqCommand
from lib.database.config import global_config
from lib.mcsmanager.instance import send_command_by_nickname, get_instance_ids
from lib.rule_registry import register


@register
class SynchronizerQqToMc(Rule):
    def __init__(self):

        super().__init__('聊天同步(qq->mc)')

    def check(self, context: Context) -> bool:
        return context.chat_session.is_qq_chat()

    async def handle(self, context: Context) -> bool:
        if not context.chat_session.is_group_chat():
            return False

        servers: List[Dict] = global_config.get('synced_servers', [])
        for server in servers:
            if not context.chat_session.session_id in server['gid']:
                continue

            # 转发逻辑
            send_command_by_nickname(server['nickname'], f'/tellraw @a "[qq:{context.sender.name}] {context.get_message()}"')

        return False


@register
class SynchronizerMcToQq(Rule):
    def __init__(self):

        super().__init__('聊天同步(mc->qq)')

    def check(self, context: Context) -> bool:
        return context.chat_session.is_mc_chat() and not context.get_message().startswith('!!')

    async def handle(self, context: Context) -> bool:
        message = context.get_message()

        nickname = context.chat_session.session_id
        servers: List[Dict] = global_config.get('synced_servers', [])
        for server in servers:
            if server['nickname'] != nickname:
                continue

            for gid in server['gid']:
                await nonebot.get_bot().send_group_msg(group_id=int(gid), message='<' + context.sender.name + '> ' + message)

        return False

@register
class Bind(QqCommand):
    def __init__(self):
        super().__init__('bnd', '绑定转发', '将本群绑定/解绑某个服务器, 需要对应服务器标签', '/bind <实例昵称>')

    def check(self, context: Context) -> bool:
        return context.get_message().startswith('/bind ')

    async def handle(self, context: Context) -> bool:
        if not context.chat_session.is_group_chat():
            await context.send_message('/bind 在私聊中不可用')
            return False

        args = context.get_message().split(' ')
        if len(args) == 1:
            await context.send_message('未知指令结构. 使用/help -u bind了解详情')
            return False

        # 先检查权限
        if context.sender.get_role() == 'USER' and not context.sender.has_tag(args[1]):
            await context.send_message('您的权限不足')
            return False

        nickname = args[1]
        try:
            get_instance_ids(nickname)
        except KeyError as e:
            await context.send_message(str(e))
            return False

        servers: List[Dict] = global_config.get('synced_servers', [])
        gid = context.chat_session.session_id

        for server in servers:
            if server['nickname'] != nickname:
                continue

            if gid in server['gid']:
                server['gid'].remove(gid)
                if len(server['gid']) == 0:
                    servers.remove(server)
                global_config.set('synced_servers', servers)
                await context.send_message(f'已解绑服务器 {nickname}')
                return False

            server['gid'].append(gid)
            global_config.set('synced_servers', servers)
            await context.send_message(f'已绑定服务器 {nickname}')
            return False

        servers.append({'nickname': nickname, 'gid': [gid]})
        global_config.set('synced_servers', servers)
        await context.send_message(f'已绑定服务器 {nickname}')
        return False
