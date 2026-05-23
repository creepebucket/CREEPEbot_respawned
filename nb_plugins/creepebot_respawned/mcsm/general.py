import time

from lib.chat.context import Context
from lib.chat.html_renderer import render
from lib.chat.rules import Command
from lib.html_files.mcsm.general import get_node_status_html, get_dashboard_html
from lib.mcsmanager import get_remote_node_list, get_overview
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

        await context.send_message(await render(get_node_status_html(response, request_time)))

@register
class McsmDashboard(Command):
    def __init__(self):
        super().__init__('dsb', 'MCSM数据', '获取MCSManager仪表盘数据', '/mcsm')

    def check(self, context: Context) -> bool:
        return context.get_message() == '/mcsm'

    async def handle(self, context: Context) -> bool:
        response = get_overview()

        await context.send_message(await render(get_dashboard_html(response)))

@register
class DaemonIdList(Command):
    def __init__(self):
        super().__init__('did', '节点Daemon ID', '获取所有节点的Daemon ID', '/mcsmdid')

    def check(self, context: Context) -> bool:
        return context.get_message() == '/mcsmdid'

    async def handle(self, context: Context) -> bool:
        await context.send_message("\n".join(remote['uuid'] for remote in get_overview()['data']['remote']))
