from lib import logger
from lib.backup import start_backup, list_backup, restore_backup
from lib.chat.context import Context
from lib.chat.rules import QqCommand
from lib.mcsmanager.instance import get_instance_cwd_by_nickname
from lib.rule_registry import register


@register
class BackupStart(QqCommand):
    def __init__(self):
        super().__init__('bks', '创建备份', '为实例的 cwd 目录创建备份', '/backup <名称> <备份名>')

    def check(self, context: Context) -> bool:
        return context.get_message().startswith('/backup ')

    async def handle(self, context: Context) -> bool:
        message = context.get_message()
        args = message.split(' ')

        if len(args) < 3 or args[1] == '' or args[2] == '':
            await context.send_message('指令格式错误! 使用/help -u /backup查看详情')
            return False

        nickname = args[1]
        backup_name = ' '.join(args[2:])

        try:
            cwd = get_instance_cwd_by_nickname(nickname)
        except KeyError:
            logger.warn(f'找不到给定实例: {nickname}')
            await context.send_message(f'找不到给定实例: {nickname}')
            return False

        doc = start_backup(cwd, backup_name)
        await context.send_message(f'备份已创建: {nickname} {doc["time"]} {doc["name"]}')
        return False


@register
class BackupList(QqCommand):
    def __init__(self):
        super().__init__('bkl', '备份列表', '查看实例的备份列表', '/backup_list <名称>')

    def check(self, context: Context) -> bool:
        return context.get_message().startswith('/backup_list ')

    async def handle(self, context: Context) -> bool:
        message = context.get_message()
        args = message.split(' ')

        if len(args) < 2 or args[1] == '':
            await context.send_message('指令格式错误! 使用/help -u /backup_list查看详情')
            return False

        nickname = args[1]

        try:
            cwd = get_instance_cwd_by_nickname(nickname)
        except KeyError:
            logger.warn(f'找不到给定实例: {nickname}')
            await context.send_message(f'找不到给定实例: {nickname}')
            return False

        backups = list_backup(cwd)
        if len(backups) == 0:
            await context.send_message(f'实例 `{nickname}` 没有备份记录')
            return False

        await context.send_message('\n'.join(f'{i["time"]} {i["name"]}' for i in backups))
        return False


@register
class BackupRestore(QqCommand):
    def __init__(self):
        super().__init__('bkr', '恢复备份', '将实例的 cwd 恢复到指定备份', '/backup_restore <名称> <time>')

    def check(self, context: Context) -> bool:
        return context.get_message().startswith('/backup_restore ')

    async def handle(self, context: Context) -> bool:
        message = context.get_message()
        args = message.split(' ')

        if len(args) < 3 or args[1] == '' or args[2] == '':
            await context.send_message('指令格式错误! 使用/help -u /backup_restore查看详情')
            return False

        nickname = args[1]
        try:
            target_time = int(args[2])
        except ValueError:
            await context.send_message('指令格式错误! 使用/help -u /backup_restore查看详情')
            return False

        try:
            cwd = get_instance_cwd_by_nickname(nickname)
        except KeyError:
            logger.warn(f'找不到给定实例: {nickname}')
            await context.send_message(f'找不到给定实例: {nickname}')
            return False

        restore_backup(cwd, target_time)
        await context.send_message(f'恢复完成: {nickname} <- {target_time}')
        return False
