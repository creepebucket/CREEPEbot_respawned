import asyncio
import hashlib
import re
from typing import List, Dict

from lib import logger
from lib.chat.Input_adapters import McInputAdapter
from lib.chat.chat_session import ChatSession
from lib.chat.context import Context
from lib.chat.output_adapters import McLogOutputHandler, McMessageOutputAdapter
from lib.database.config import PersonalConfig
from lib.mcsmanager.instance import get_output_log_by_nickname, get_all_instance_nicknames
from message_source.api import distribute_event

log_hashes: Dict = {}

def get_logs_hash(logs: List[str]) -> str:
    return hashlib.md5('\n'.join(logs).encode()).hexdigest()


async def sync():
    sender = PersonalConfig(0)
    for nickname in get_all_instance_nicknames():
        logs: List = get_output_log_by_nickname(nickname)['data'].splitlines()

        if nickname not in log_hashes:
            log_hashes[nickname] = get_logs_hash(logs[-5:])
            continue

        new = []
        for i in range(len(logs), 4, -1):
            if get_logs_hash(logs[i - 5:i]) != log_hashes[nickname]:
                continue
            new = logs[i:]
            break

        for log in new:
            if '[qq:' in log:
                continue

            logger.info(f'收到来自**mc服务器**`{nickname}`的日志: `{log}`')

            await distribute_event(Context(McInputAdapter(log), McLogOutputHandler(nickname), ChatSession(nickname, 'mc_log'), sender))
            if re.search(r'].*?<([\w\\-]+)> (.*)', log):
                message = re.search(r'].*?<[\w\\-]+> (.*)', log).group(1)
                sender = re.search(r'].*?<([\w\\-]+)> .*', log).group(1)
                await distribute_event(Context(McInputAdapter(message), McMessageOutputAdapter(nickname, sender), ChatSession(nickname, 'mc_chat'), PersonalConfig(sender)))

        log_hashes[nickname] = get_logs_hash(logs[-5:])


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
