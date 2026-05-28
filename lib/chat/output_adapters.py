from abc import ABC, abstractmethod

from nonebot.adapters.onebot.v11 import Event, Bot
from nonebot.adapters.onebot.v11.event import Sender
from nonebot.internal.matcher import Matcher

from lib.mcsmanager.instance import send_command_by_nickname


class OutputAdapter(ABC):
    @abstractmethod
    async def send_message(self, message):
        pass

class QqOutputAdapter(OutputAdapter):
    def __init__(self, bot: Bot, event: Event, handler: type[Matcher]):
        self.bot = bot
        self.event = event
        self.handler = handler

    async def send_message(self, message):
        await self.handler.send(message)

class McLogOutputHandler(OutputAdapter):
    def __init__(self, nickname: str):
        self.nickname = nickname

    async def send_message(self, message):
        send_command_by_nickname(self.nickname, f'/tellraw @a "[creepebot] {message}"')

class McMessageOutputAdapter(OutputAdapter):
    def __init__(self, nickname: str, sender: str):
        self.nickname = nickname
        self.sender = sender

    async def send_message(self, message):
        send_command_by_nickname(self.nickname, f'/tellraw {self.sender} "{message}"')