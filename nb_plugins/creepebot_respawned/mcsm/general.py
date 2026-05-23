import time

from lib.chat.context import Context
from lib.chat.html_renderer import render
from lib.chat.rules import Command
from lib.html_files.mcsm.general import generate_node_status_html
from lib.mcsmanager import get_remote_node_list
from lib.rule_registry import register


@register
class RemoteNodeData(Command):
    def __init__(self):
        super().__init__('rnd', '远程节点信息', '获取MCSManager的远程节点信息', '/mcsmrnd')

    def check(self, context: Context) -> bool:
        return context.get_message() == '/mcsmrnd'

    async def handle(self, context: Context) -> bool:
        request_time = time.time()
        response = get_remote_node_list()

        await context.send_message(await render(generate_node_status_html(response, request_time)))