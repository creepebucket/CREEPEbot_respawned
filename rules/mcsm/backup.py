from lib import logger
from lib.backup import start_backup, list_backup, restore_backup
from lib.backup.auto import (
    format_auto_backup_task,
    get_auto_backup_task,
    get_auto_backup_tasks,
    run_auto_backup_now,
    set_auto_backup_enabled,
    upsert_auto_backup_task,
)
from lib.chat.context import Context
from lib.chat.rules import QqCommand
from lib.mcsmanager.instance import get_instance_cwd_by_nickname
from lib.rule_registry import register


@register
class BackupStart(QqCommand):
    def __init__(self):
        super().__init__('bks', '创建备份', '为实例的 cwd 目录创建备份', '/back <名称> <备份名>')

    def check(self, context: Context) -> bool:
        return context.get_message().startswith('/back ')

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
        super().__init__('bkl', '备份列表', '查看实例的备份列表', '/backlist <名称>')

    def check(self, context: Context) -> bool:
        return context.get_message().startswith('/backlist ')

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
        super().__init__('bkr', '恢复备份', '将实例的 cwd 恢复到指定备份', '/restore <名称> <time>')

    def check(self, context: Context) -> bool:
        return context.get_message().startswith('/restore ')

    async def handle(self, context: Context) -> bool:
        message = context.get_message()
        args = message.split(' ')

        if len(args) < 3 or args[1] == '' or args[2] == '':
            await context.send_message('指令格式错误! 使用/help -u /restore查看详情')
            return False

        nickname = args[1]
        try:
            target_time = int(args[2])
        except ValueError:
            await context.send_message('指令格式错误! 使用/help -u /restore查看详情')
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


@register
class AutoBackup(QqCommand):
    def __init__(self):
        super().__init__(
            'abk',
            '自动备份',
            '管理实例自动备份配置 默认 keep=24 prefix=auto)，群聊需先 /cmd -e abk',
            '/aback | /aback <实例> | /aback <实例> status | /aback <实例> on <min> [keep=24] [prefix=auto] | /aback <实例> off | /aback <实例> run',
        )

    def check(self, context: Context) -> bool:
        return context.get_message().startswith('/aback')

    async def handle(self, context: Context) -> bool:
        message = context.get_message()
        args = message.split(' ')

        if message in ('/aback', '/auto_backup'):
            tasks = get_auto_backup_tasks()
            if len(tasks) == 0:
                await context.send_message('未配置自动备份')
                return False

            lines = []
            for t in tasks:
                lines.append(f'{t["nickname"]} {"on" if t["enabled"] else "off"} {t["interval_min"]}m keep={t["keep"]} next={t["next_time"]}')
            await context.send_message('\n'.join(lines))
            return False

        if len(args) == 2 and args[1] != '':
            await context.send_message(format_auto_backup_task(get_auto_backup_task(args[1])))
            return False

        if len(args) < 3 or args[1] == '' or args[2] == '':
            await context.send_message('指令格式错误! 使用/help -u /aback查看详情')
            return False

        nickname = args[1]
        action = args[2]

        if action == 'status':
            await context.send_message(format_auto_backup_task(get_auto_backup_task(nickname)))
            return False

        if action == 'off':
            task = set_auto_backup_enabled(nickname, False)
            await context.send_message('已关闭自动备份\n' + format_auto_backup_task(task))
            return False

        if action == 'run':
            doc = await run_auto_backup_now(nickname)
            await context.send_message(f'备份已创建: {nickname} {doc["time"]} {doc["name"]}')
            return False

        if action == 'on':
            if len(args) < 4 or args[3] == '':
                await context.send_message('指令格式错误! 使用/help -u /aback查看详情')
                return False

            try:
                interval_min = int(args[3])
            except ValueError:
                await context.send_message('interval_min 必须是数字')
                return False

            keep = 24
            if len(args) >= 5 and args[4] != '':
                try:
                    keep = int(args[4])
                except ValueError:
                    await context.send_message('keep 必须是数字')
                    return False

            prefix = 'auto'
            if len(args) >= 6 and args[5] != '':
                prefix = ' '.join(args[5:])

            task = upsert_auto_backup_task(nickname, True, interval_min, keep, prefix)
            await context.send_message('已开启自动备份\n' + format_auto_backup_task(task))
            return False

        await context.send_message('用法: /aback [实例] [status|on|off|run] ...')
        return False
