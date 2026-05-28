from lib.backup import start_backup, list_backup, restore_backup
from lib.chat.context import Context
from lib.chat.rule import Rule
from lib.mcsmanager.instance import get_instance_cwd_by_nickname
from lib.rule_registry import register


@register
class InGameBackup(Rule):
    def __init__(self):
        super().__init__('游戏内备份')

    def check(self, context: Context) -> bool:
        return context.chat_session.is_mc_chat() and context.get_message().startswith('!!back')

    async def handle(self, context: Context) -> bool:
        message = context.get_message()
        args = message.split(' ')

        nickname = context.chat_session.session_id
        cwd = get_instance_cwd_by_nickname(nickname)

        if message in ('!!back', '!!back list'):
            backups = list_backup(cwd)
            if len(backups) == 0:
                await context.send_message('没有备份记录')
                return False

            await context.send_message(' | '.join(f'{i["time"]} {i["name"]}' for i in backups[:5]))
            return False

        if len(args) >= 3 and args[1] == 'start' and args[2] != '':
            doc = start_backup(cwd, ' '.join(args[2:]))
            await context.send_message(f'备份已创建: {doc["time"]} {doc["name"]}')
            return False

        if len(args) == 3 and args[1] == 'restore' and args[2] != '':
            try:
                restore_backup(cwd, int(args[2]))
            except ValueError:
                await context.send_message('time 必须是数字')
                return False

            await context.send_message(f'恢复完成: {args[2]}')
            return False

        await context.send_message('用法: !!back [list] | !!back start <name> | !!back restore <time>')
        return False
