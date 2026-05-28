import asyncio

import nonebot
from nonebot.adapters.onebot.v11 import Bot

from lib import logger
from lib.database.config import MongoConfig


class ChatSession(MongoConfig):
    """
    聊天会话基类, 用于群聊, 私聊等场景的权限管理和配置
    """

    def __init__(self, session_id, session_type: str):
        """
        构造函数
        :param session_id: 会话id(群号等)
        :param session_type: 会话类型(群聊group, 私聊private等)
        """

        self.session_id = session_id
        self.session_type = session_type
        super().__init__(f'local_session_{session_type}_{session_id}')

    def is_group_chat(self) -> bool:
        return self.session_type == 'group'

    def is_private_chat(self) -> bool:
        return self.session_type == 'private'

    def is_mc_chat(self) -> bool:
        return self.session_type == 'mc_chat'

    def is_chat(self) -> bool:
        return self.is_mc_chat() or self.is_group_chat() or self.is_private_chat()

    def is_qq_chat(self):
        return self.is_private_chat() or self.is_group_chat()

    def is_mc_log(self) -> bool:
        return self.session_type == 'mc_log'

    async def get_permission(self, user: int) -> int:
        """
        获取用户权限 私聊默认满足所有权限
        :param user: 用户qq号
        :return: 权限(0 - 10)
        """

        if self.is_private_chat():
            return 10

        elif self.is_group_chat():
             perm: int = self.get(f'user_permissions/{user}', -1)

             if perm != -1: return perm

             # 如果数据库无记录，进行群角色检测
             bot: Bot = nonebot.get_bot()

             try:
                 member_info = await bot.get_group_member_info(
                     group_id=self.session_id,
                     user_id=user
                 )
             except (TimeoutError, asyncio.TimeoutError):
                 # 处理超时情况

                 logger.warn(f'在处理会话 `{self.session_id}` ('
                             f'{'群聊' if self.is_group_chat() else '私聊' if self.is_private_chat() else '其他'})'
                             f' 对 {user} 的权限获取时超时')
                 return 0

             role = member_info.get("role", "member")

             # 根据角色设置权限
             if role == "owner":
                 permission = 5
             elif role == "admin":
                 permission = 3
             else:
                 permission = 0

             # 将权限保存到数据库
             self.set_permission(user, permission)
             return permission

        return 0


    def set_permission(self, user: int, permission: int) -> None:
        """
        设置某个用户的权限, 私聊没有作用
        :param user: 用户qq号
        :param permission: 权限(0 - 10)
        """

        if self.is_group_chat(): self.set(f'user_permissions/{user}', permission)

    def is_rule_enabled(self, command: str) -> bool:
        """
        是否启动了消息处理器 (私聊永远True)
        :param command: 指令
        :return: 结果
        """

        return self.is_private_chat() or self.get(f'command_statuses/{command}', False)

    async def mute(self, user: int, duration_sec: int) -> None:
        """
        禁言群成员
        :param user: 被禁言的用户QQ号
        :param duration_sec: 禁言时长，单位为秒
        """

        if not self.is_group_chat(): return
        bot = nonebot.get_bot()
        await bot.set_group_ban(group_id=self.session_id, user_id=user, duration=duration_sec)

    async def unmute(self, user: int) -> None:
        """
        解除群成员禁言
        :param user: 被解除禁言的用户QQ号
        """

        if not self.is_group_chat(): return
        bot = nonebot.get_bot()
        await bot.set_group_ban(group_id=self.session_id, user_id=user, duration=0)

    async def kick(self, user: int) -> None:
        """
        将群成员踢出群
        :param user: 被踢出的用户QQ号
        """

        if not self.is_group_chat(): return
        bot = nonebot.get_bot()
        await bot.set_group_kick(group_id=self.session_id, user_id=user, reject_add_request=False)

    async def ban(self, user: int) -> None:
        """
        将群成员拉黑
        :param user: 被拉黑的用户QQ号
        """

        if not self.is_group_chat(): return
        bot = nonebot.get_bot()
        await bot.set_group_kick(group_id=self.session_id, user_id=user, reject_add_request=True)

    async def set_nickname(self, user: int, nickname: str) -> None:
        """
        设置群成员昵称
        :param user: 要设置昵称的用户QQ号
        :param nickname: 昵称
        """

        if not self.is_group_chat(): return
        bot = nonebot.get_bot()
        await bot.set_group_card(group_id=self.session_id, user_id=user, card=nickname)

    def set_rule_status(self, command: str, status: bool) -> None:
        """
        设置消息处理器状态(启用/禁用) 私聊没有反应
        :param command: 指令
        :param status: 状态
        """

        if self.is_group_chat(): self.set(f'command_statuses/{command}', status)
