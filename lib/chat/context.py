from sympy.strategies.core import switch

from lib.chat.Input_adapters import InputAdapter, QqInputAdapter
from lib.chat.chat_session import ChatSession
from lib.chat.output_adapters import OutputAdapter, QqOutputAdapter
from lib.database.config import PersonalConfig
from nonebot.adapters.onebot.v11 import Event, Bot
from nonebot.internal.matcher import Matcher


class Context:
    def __init__(self, input_adapter: InputAdapter, output_adapter: OutputAdapter, chat_session: ChatSession, sender: PersonalConfig):
        self.input_adapter = input_adapter
        self.output_adapter = output_adapter
        self.chat_session = chat_session
        self.sender = sender

    def get_message(self) -> str:
        return self.input_adapter.get_message_rich_text()

    async def send_message(self, message: str):
        await self.output_adapter.send_message(message)
