import re

from lib import logger
from lib.chat.context import Context
from lib.chat.html_renderer import render
from lib.chat.rules import Command
from lib.html_files.mcsm.instance import render_instance_list, get_log_html
from lib.mcsmanager import get_overview, get_instance_list
from lib.mcsmanager.instance import start_instance_by_nickname, stop_instance_by_nickname, restart_instance_by_nickname
from lib.mcsmanager.instance import kill_instance_by_nickname, send_command_by_nickname
from lib.mcsmanager.instance import get_output_log_by_nickname
from lib.rule_registry import register


@register
class InstanceList(Command):
    def __init__(self):
        super().__init__('lst', '实例列表', '获取 MCSManager 所有实例列表', '/list')

    def check(self, context: Context) -> bool:
        return context.get_message() == '/list'

    async def handle(self, context: Context) -> bool:
        overview = get_overview()
        daemon_list = overview['data']['remote']

        instances = []
        for daemon in daemon_list:
            resp = get_instance_list(daemonId=daemon['uuid'], status='', page=1, page_size=100)
            max_page = resp['data']['maxPage']
            instances += resp['data']['data']

            for page in range(2, max_page + 1):
                resp = get_instance_list(daemonId=daemon['uuid'], status='', page=page, page_size=100)
                instances += resp['data']['data']

        await context.send_message(await render(render_instance_list(instances)))
        return False


@register
class InstanceStart(Command):
    def __init__(self):
        super().__init__('sta', '启动实例', '启动目标实例', '/start <名称>')

    def check(self, context: Context) -> bool:
        return context.get_message().startswith('/start ')

    async def handle(self, context: Context) -> bool:
        message = context.get_message()
        args = message.split(' ')
        if len(args) < 2 or args[1] == '':
            await context.send_message('指令格式错误! 使用/help -u /start查看详情')
            return False
        nickname = args[1]

        try:
            start_instance_by_nickname(nickname)
        except KeyError:
            logger.warn(f'找不到给定实例: {nickname}')
            await context.send_message(f'找不到给定实例: {nickname}')
            return False

        await context.send_message(f'已提交启动请求: {nickname}')
        return False


@register
class InstanceStop(Command):
    def __init__(self):
        super().__init__('stp', '停止实例', '安全停止实例', '/stop <名称>')

    def check(self, context: Context) -> bool:
        return context.get_message().startswith('/stop ')

    async def handle(self, context: Context) -> bool:
        message = context.get_message()
        args = message.split(' ')
        if len(args) < 2 or args[1] == '':
            await context.send_message('指令格式错误! 使用/help -u /stop查看详情')
            return False
        nickname = args[1]

        try:
            stop_instance_by_nickname(nickname)
        except KeyError:
            logger.warn(f'找不到给定实例: {nickname}')
            await context.send_message(f'找不到给定实例: {nickname}')
            return False

        await context.send_message(f'已提交停止请求: {nickname}')
        return False


@register
class InstanceRestart(Command):
    def __init__(self):
        super().__init__('rst', '重启实例', '重新启动实例', '/restart <名称>')

    def check(self, context: Context) -> bool:
        return context.get_message().startswith('/restart ')

    async def handle(self, context: Context) -> bool:
        message = context.get_message()
        args = message.split(' ')
        if len(args) < 2 or args[1] == '':
            await context.send_message('指令格式错误! 使用/help -u /restart查看详情')
            return False
        nickname = args[1]

        try:
            restart_instance_by_nickname(nickname)
        except KeyError:
            logger.warn(f'找不到给定实例: {nickname}')
            await context.send_message(f'找不到给定实例: {nickname}')
            return False

        await context.send_message(f'已提交重启请求: {nickname}')
        return False


@register
class InstanceKill(Command):
    def __init__(self):
        super().__init__('kil', '强制终止', '强制终止实例进程', '/kill <名称>')

    def check(self, context: Context) -> bool:
        return context.get_message().startswith('/kill ')

    async def handle(self, context: Context) -> bool:
        message = context.get_message()
        args = message.split(' ')
        if len(args) < 2 or args[1] == '':
            await context.send_message('指令格式错误! 使用/help -u /kill查看详情')
            return False
        nickname = args[1]

        try:
            kill_instance_by_nickname(nickname)
        except KeyError:
            logger.warn(f'找不到给定实例: {nickname}')
            await context.send_message(f'找不到给定实例: {nickname}')
            return False

        await context.send_message(f'已提交强制终止请求: {nickname}')
        return False


@register
class InstanceSend(Command):
    def __init__(self):
        super().__init__('snd', '发送命令', '向后台发送命令', '/send <名称> <指令>')

    def check(self, context: Context) -> bool:
        return context.get_message().startswith('/send ')

    async def handle(self, context: Context) -> bool:
        message = context.get_message()
        args = message.split(' ')
        if len(args) < 3 or args[1] == '':
            await context.send_message('指令格式错误! 使用/help -u /send查看详情')
            return False

        nickname = args[1]
        command = ' '.join(args[2:])
        if command == '':
            await context.send_message('指令格式错误! 使用/help -u /send查看详情')
            return False

        try:
            send_command_by_nickname(nickname, command)
        except KeyError:
            logger.warn(f'找不到给定实例: {nickname}')
            await context.send_message(f'找不到给定实例: {nickname}')
            return False

        await context.send_message(f'已发送: {nickname} <- {command}')
        return False


@register
class InstanceLog(Command):
    def __init__(self):
        super().__init__('log', '实例日志', '获取实例输出日志', '/log <名称> <行数>')

    def check(self, context: Context) -> bool:
        return context.get_message().startswith('/log ')

    async def handle(self, context: Context) -> bool:
        message = context.get_message()
        args = message.split(' ')
        if len(args) < 3 or args[1] == '' or args[2] == '':
            await context.send_message('指令格式错误! 使用/help -u /log查看详情')
            return False

        nickname = args[1]
        try:
            size = int(args[2])
            if size > 200:
                await context.send_message(f'最大显示行数为200, 当前: {size}')
                return False

        except ValueError:
            await context.send_message('指令格式错误! 使用/help -u /log查看详情')
            return False

        try:
            resp = get_output_log_by_nickname(nickname)
        except KeyError:
            logger.warn(f'找不到给定实例: {nickname}')
            await context.send_message(f'找不到给定实例: {nickname}')
            return False

        await context.send_message(await render(get_log_html('\n'.join(resp['data'].splitlines()[-size:]), nickname)))
        return False
