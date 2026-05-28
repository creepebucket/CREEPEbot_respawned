from lib.backup.auto import (
    format_auto_backup_task,
    get_auto_backup_task,
    run_auto_backup_now,
    set_auto_backup_enabled,
    upsert_auto_backup_task,
)
from lib.chat.context import Context
from lib.chat.rule import Rule
from lib.rule_registry import register


@register
class InGameAutoBackup(Rule):
    def __init__(self):
        super().__init__('游戏内自动备份')

    def check(self, context: Context) -> bool:
        return context.chat_session.is_mc_chat() and context.get_message().startswith('!!aback')

    async def handle(self, context: Context) -> bool:
        message = context.get_message()
        args = message.split(' ')

        nickname = context.chat_session.session_id

        if message in ('!!aback', '!!aback status'):
            await context.send_message(format_auto_backup_task(get_auto_backup_task(nickname)))
            return False

        if len(args) >= 2 and args[1] == 'off':
            task = set_auto_backup_enabled(nickname, False)
            await context.send_message('已关闭自动备份\n' + format_auto_backup_task(task))
            return False

        if len(args) >= 2 and args[1] == 'run':
            doc = await run_auto_backup_now(nickname)
            await context.send_message(f'备份已创建: {doc["time"]} {doc["name"]}')
            return False

        if len(args) >= 3 and args[1] == 'on' and args[2] != '':
            try:
                interval_min = int(args[2])
            except ValueError:
                await context.send_message('interval_min 必须是数字')
                return False

            keep = 24
            if len(args) >= 4 and args[3] != '':
                try:
                    keep = int(args[3])
                except ValueError:
                    await context.send_message('keep 必须是数字')
                    return False

            prefix = 'auto'
            if len(args) >= 5 and args[4] != '':
                prefix = ' '.join(args[4:])

            task = upsert_auto_backup_task(nickname, True, interval_min, keep, prefix)
            await context.send_message('已开启自动备份\n' + format_auto_backup_task(task))
            return False

        await context.send_message('用法: !!aback [status] | !!aback on <min> [keep] [prefix] | !!aback off | !!aback run')
        return False

