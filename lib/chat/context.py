from nonebot.adapters.onebot.v11 import Event, Bot
from nonebot.internal.matcher import Matcher

from lib.chat.chat_session import ChatSession
from lib.database.config import PersonalConfig


class Context:
    def __init__(self, bot: Bot, event: Event, handler: type[Matcher]):
        self.bot = bot
        self.event = event
        self.handler = handler

    def get_message(self):
        """
        获取信息文本(at等消息已转义)
        :return: 文本
        """

        message = self.event.original_message
        parts: list[str] = []

        for segment in message:
            if isinstance(segment, str):
                parts.append(segment)
                continue

            seg_type = getattr(segment, "type", None)
            data = getattr(segment, "data", None) or {}

            if seg_type == "text":
                parts.append(str(data.get("text", "")))
                continue

            if seg_type == "image":
                parts.append("[image]")
                continue

            if seg_type == "at":
                qq = data.get("qq")
                parts.append(f"[at:{qq}]" if qq is not None else "[at]")
                continue

            if seg_type == "reply":
                reply_id = data.get("id")
                parts.append(f"[reply:{reply_id}]" if reply_id is not None else "[reply]")
                continue

            if seg_type:
                if "id" in data:
                    parts.append(f"[{seg_type}:{data['id']}]")
                elif "qq" in data:
                    parts.append(f"[{seg_type}:{data['qq']}]")
                else:
                    parts.append(f"[{seg_type}]")
            else:
                parts.append(str(segment))

        return "".join(parts)

    async def send_message(self, message):
        await self.handler.send(message)

    @property
    def chat_session(self) -> ChatSession:
        """
        获取当前消息的会话对象(群聊/私聊)
        :return:
        """
        if hasattr(self, "_chat_session"):
            return self._chat_session

        message_type = getattr(self.event, "message_type", None)

        if message_type == "group":
            session_type = "group"
            session_id = int(getattr(self.event, "group_id"))
        else:
            session_type = "private"
            session_id = int(getattr(self.event, "user_id", None) or self.event.get_user_id())

        self._chat_session = ChatSession(session_id, session_type)
        return self._chat_session

    @property
    def sender(self) -> PersonalConfig:
        """
        获取消息发送者
        :return:
        """
        if hasattr(self, "_sender"):
            return self._sender

        config = PersonalConfig(int(getattr(self.event, "user_id", None) or self.event.get_user_id()))
        self._sender = config

        return config