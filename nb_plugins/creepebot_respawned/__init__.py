import traceback

from nonebot import on_message
from nonebot.adapters.onebot.v11 import Bot, Event

from lib import logger
from lib.chat.context import Context
from lib.logger import colored
from lib.rule_registry import get_registry

message_handler = on_message()

@message_handler.handle()
async def got_message(bot: Bot, event: Event):
    registries = get_registry()

    # 构建Context
    context = Context(bot, event, message_handler)

    for rule in registries:

        try:
            if rule.check(context):
                logger.debug(f'此条消息已被处理器 `{rule.name}` ({rule}) 处理')

                if await rule.handle(context):
                    break
        except Exception as e:
            traceback_blank_line = (colored('\n---------- --------', 'dark_green') + ' | '
                                  + colored('ERRO', 'orange') + ' | ' + '[traceback] '
                                  + '-' * 38 + colored(' | ', 'cyan'))

            logger.error(f'在处理处理器 `{rule.name}` ({rule}) 逻辑时**报错**: {traceback_blank_line}'
                         + colored(type(e).__name__ + ': ' + str(e), 'red')
                         + traceback_blank_line.join(traceback.format_exc().split('\n')))
