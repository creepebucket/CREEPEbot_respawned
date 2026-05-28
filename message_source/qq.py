import traceback

from nonebot import on_message
from nonebot.adapters.onebot.v11 import Bot, Event

from lib.chat.Input_adapters import QqInputAdapter
from lib.chat.chat_session import ChatSession
from lib.chat.context import Context
from lib.chat.output_adapters import QqOutputAdapter
from lib.database.config import PersonalConfig
from message_source.api import distribute_event

message_handler = on_message()

@message_handler.handle()
async def got_message(bot: Bot, event: Event):

    # 构建Context
    message_type = getattr(event, "message_type", None)

    if message_type == "group":
        session_type = "group"
        session_id = int(getattr(event, "group_id"))
    else:
        session_type = "private"
        session_id = int(getattr(event, "user_id", None) or event.get_user_id())

    chat_session = ChatSession(session_id, session_type)

    config = PersonalConfig(int(getattr(event, "user_id", None) or event.get_user_id()))
    sender = config

    input_adapter = QqInputAdapter(bot, event, message_handler)
    output_adapter = QqOutputAdapter(bot, event, message_handler)

    await distribute_event(Context(input_adapter, output_adapter, chat_session, sender))
