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
                if hasattr(rule, 'id') and not rule.bypass_enable_check and not context.chat_session.is_rule_enabled(rule.id):
                    logger.debug(f'此条消息已被处理器 `{rule.name}` ({rule}) 识别, 但该会话 `{context.chat_session.session_id}` '
                                 f'({'群聊' if context.chat_session.is_group_chat() else '私聊'}) 已**禁用**此处理器')

                    continue

                logger.debug(f'此条消息已被处理器 `{rule.name}` ({rule}) 处理')

                if await rule.handle(context):
                    break
        except Exception as e:
            traceback_blank_line = (colored('\n---------- --------', 'dark_green') + ' | '
                                  + colored('ERRO', 'orange') + ' | ' + '[traceback] '
                                  + '-' * 38 + colored(' | ', 'cyan'))

            logger.error(f'在处理处理器 `{rule.name}` ({rule}) 逻辑时**报错**: {traceback_blank_line}'
                         + colored(type(e).__name__ + ': ' + str(e), 'red' + ' ')
                         + traceback_blank_line.join(traceback.format_exc().split('\n')))
