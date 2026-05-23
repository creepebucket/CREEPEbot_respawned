import asyncio
import hashlib
import re
from typing import List, Dict

import nonebot

from lib.chat.context import Context
from lib.chat.rule import Rule
from lib.chat.rules import Command
from lib.database.config import global_config
from lib.mcsmanager.instance import get_instance_ids, get_output_log_by_nickname, send_command_by_nickname
from lib.rule_registry import register

log_hashes: Dict = {}

def get_logs_hash(logs: List[str]) -> str:
    return hashlib.md5('\n'.join(logs).encode()).hexdigest()


async def sync():
    # 获取所有需要转发的服务器

    servers: List[Dict] = global_config.get('synced_servers', [])

    for server in servers:
        gids: List[int] = server['gid']
        nickname: str = server['nickname']

        # 获取最新log
        logs: List = get_output_log_by_nickname(nickname)['data'].splitlines()

        # 检查hash是否存在
        if not nickname in log_hashes.keys():
            # 选取最后5行
            log_hashes[nickname] = get_logs_hash(logs[-5:])
            continue

        new = []
        for i in range(len(logs), 4, -1):
            if get_logs_hash(logs[i - 5:i]) != log_hashes[nickname]:
                continue
            new = logs[i:]
            break

        for log in new:
            match = re.search(r'\].*?<(\w+)> (.*)', log)

            if not match:
                continue

            # 需要检查是否有qq转发消息回传的情况
            if '[qq:' in log:
                continue

            player, message = match.groups()
            for gid in gids:
                await nonebot.get_bot().send_group_msg(group_id=int(gid), message='<' + player + '> ' + message)

        # 更新hash缓存
        log_hashes[nickname] = get_logs_hash(logs[-5:])


@register
class Synchronizer(Rule):
    def __init__(self):

        super().__init__('聊天同步')

    def check(self, context: Context) -> bool:
        return True

    async def handle(self, context: Context) -> bool:
        if not context.chat_session.is_group_chat():
            return False

        servers: List[Dict] = global_config.get('synced_servers', [])
        for server in servers:
            if not context.chat_session.session_id in server['gid']:
                continue

            # 转发逻辑
            send_command_by_nickname(server['nickname'], f'/tellraw @a "[qq:{context.sender.qid}] {context.get_message()}"')

        return False

@register
class Bind(Command):
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


async def periodic_caller(func, interval):
    """固定间隔启动 func，串行执行，超时则立即开始下一次"""

    await asyncio.sleep(1)

    next_start = asyncio.get_event_loop().time()  # 第一次立即执行
    while True:
        now = asyncio.get_event_loop().time()
        delay = next_start - now
        if delay > 0:
            await asyncio.sleep(delay)

        start_time = asyncio.get_event_loop().time()
        await func()
        next_start = start_time + interval


async def start_sync():
    asyncio.create_task(periodic_caller(sync, 1))
