from nonebot.adapters.onebot.v11 import Event, Bot
from nonebot.internal.matcher import Matcher


class Context:
    def __init__(self, bot: Bot, event: Event, handler: type[Matcher]):
        self.bot = bot
        self.event = event
        self.handler = handler

    def get_message_text(self):
        message = self.event.get_message()
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
