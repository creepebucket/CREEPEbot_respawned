import re
import sys
import time

from nonebot.log import logger, logger_id, default_filter
from datetime import datetime


log_level: int = 0

def rgb_to_ansi(r: int, g: int, b: int, background=False) -> str:
    """
    将 RGB 颜色转换为 ANSI 转义码（真彩色）。

    参数:
        r, g, b: 0-255 之间的整数
        background: 若为 True 则生成背景色转义码，否则生成前景色转义码

    返回:
        以 '\033[...m' 开头的 ANSI 转义码字符串
    """
    # 钳位输入值到 0-255
    r = max(0, min(255, r))
    g = max(0, min(255, g))
    b = max(0, min(255, b))

    if background:
        return f'\033[48;2;{r};{g};{b}m'
    else:
        return f'\033[38;2;{r};{g};{b}m'


def colored_rgb(text: str, r: int, g: int, b: int, background=False) -> str:
    """
    返回带有指定 RGB 颜色的字符串（已包含重置码）。

    示例: print(colored_text("Hello", 255, 0, 0))   -> 红色 Hello
    """
    start = rgb_to_ansi(r, g, b, background)
    reset = '\033[0m'
    return f"{start}{text}{reset}"

def colored(text: str, color: str) -> str:

    if   'red'    in color: r = 255; g =  0  ; b = 0
    elif 'green'  in color: r = 0  ; g =  255; b = 0
    elif 'blue'   in color: r = 0  ; g =  0  ; b = 255
    elif 'yellow' in color: r = 255; g =  255; b = 0
    elif 'orange' in color: r = 255; g =  128; b = 0
    elif 'cyan'   in color: r = 0  ; g =  255; b = 255
    elif 'purple' in color: r = 255; g =  0  ; b = 255
    elif 'gray'   in color: r = 128; g =  128; b = 128
    elif 'black'  in color: r = 0  ; g =  0  ; b = 0
    elif 'white'  in color: r = 255; g =  255; b = 255
    else:
        raise Exception

    if   'light' in color: r = int(r / 2 + 128); g = int(g / 2 + 128); b = int(b / 2 + 128)
    elif 'dark'  in color: r = int(r / 2);       g = int(g / 2);       b = int(b / 2)

    return colored_rgb(text, r, g, b)

def inject_nonebot_logger():
    # 1. 移除 NoneBot 默认的控制台处理器
    logger.remove(logger_id)

    # 2. 定义自定义处理函数
    def custom_sink(record):
        stack = re.search(r'.*-.*-.* \| .* \| (.*) - ', record).group(1)
        stack = '[Nonebot] ' + adjust_left(stack, 40)

        message = re.search(r'.*-.*-.* - (.*)', record).group(1)

        # nonebot加载
        if message == 'NoneBot is initializing...':
            log('Nonebot正在启动...', 0, stack)

        # 加载到插件
        elif message.startswith('Succeeded to load plugin '):
            plugin = re.search('.*"(.*)".*', message).group(1)
            log(f'**成功**加载插件 `{plugin}`', 1, stack)

        # bot连接
        elif re.match('OneBot V11 \| Bot (.*) connected', message):
            bot = re.search('OneBot V11 \| Bot (.*) connected', message).group(1)
            log(f'**喜报**! bot `{bot}` 成功连接', 1, stack)

        # 接收到群消息
        elif re.match("OneBot V11 .* \| \[message.group.normal]: Message .* from .*@\[群:.*] '.*'", message):
            bot = re.search("OneBot V11 (.*) \| \[message.group.normal]: Message .* from .*@\[群:.*] '.*'", message).group(1)
            sender = re.search("OneBot V11 .* \| \[message.group.normal]: Message .* from (.*)@\[群:.*] '.*'", message).group(1)
            group = re.search("OneBot V11 .* \| \[message.group.normal]: Message .* from .*@\[群:(.*)] '.*'", message).group(1)
            content = re.search("OneBot V11 .* \| \[message.group.normal]: Message .* from .*@\[群:.*] '(.*)'", message).group(1)
            id = re.search("OneBot V11 .* \| \[message.group.normal]: Message (.*) from .*@\[群:.*] '.*'", message).group(1)

            log(f'BOT `{bot}` 接受到 由 `{sender}` 在 `{group}` 发送的**群聊**消息: `{content}` , 消息id: `{id}`', 1, stack)

        # 接收到私聊消息
        elif re.match("OneBot V11 .* \| \[message.private.friend]: Message .* from .* '.*'", message):
            bot = re.search("OneBot V11 (.*) \| \[message.private.friend]: Message .* from .* '.*'", message).group(1)
            id = re.search("OneBot V11 .* \| \[message.private.friend]: Message (.*) from .* '.*'", message).group(1)
            sender = re.search("OneBot V11 .* \| \[message.private.friend]: Message .* from (.*) '.*'", message).group(1)
            content = re.search("OneBot V11 .* \| \[message.private.friend]: Message .* from .* '(.*)'", message).group(1)

            log(f'BOT `{bot}` 接受到 由 `{sender}` 发送的**私聊**消息: `{content}` , 消息id: `{id}`', 1, stack)

        else:
            log(message, 0, stack)

    logger.add(custom_sink,level=0,filter=default_filter,serialize=False)

def set_log_level(level: str):
    global log_level

    if level == 'debug': log_level = 0
    elif level == 'info': log_level = 1
    elif level == 'warn': log_level = 2
    elif level == 'error': log_level = 3
    elif level == 'crit': log_level = 4

def get_stack() -> str:
    frame = sys._getframe(3)
    filename = frame.f_code.co_filename
    lineno = frame.f_lineno
    func_name = frame.f_code.co_name
    return f"{filename}:{lineno} {func_name}()"

def adjust_left(s: str, n: int) -> str:
    """若s长度大于n，则左截断至最后n个字符；否则左侧补空格至长度n"""
    if len(s) > n:
        return s[-n:]          # 取右侧n个字符
    else:
        return s.rjust(n)      # 左侧填充空格至长度n

def parse_markdown(text: str) -> str:
    # 粗体
    text = re.sub(r'\*\*(.*?)\*\*', lambda m: f"\033[1m{m.group(1)}\033[0m", text)
    # 强调
    text = re.sub(r'`(.*?)`', lambda m: colored(m.group(1), 'light_yellow'), text)

    return text


def log(message: str, level: int=0, stack: str=None) -> None:
    if stack == None: stack = get_stack()

    level_to_string = ['DEBU', 'INFO', 'WARN', 'ERRO', 'CRIT']
    level_color = ['cyan', 'white', 'yellow', 'orange', 'red']

    print(
          colored(time.strftime("%Y-%m-%d %H:%M:%S"), 'dark_green')
        + ' | '
        + colored(level_to_string[level], level_color[level])
        + ' | '
        + adjust_left(stack, 50)
        + colored(' | ', 'cyan')
        + parse_markdown(message)
    )

def debug(message: str) -> None:
    if log_level <= 0: log(message, 0)

def info(message: str) -> None:
    if log_level <= 1: log(message, 1)

def warn(message: str) -> None:
    if log_level <= 2: log(message, 2)

def error(message: str) -> None:
    if log_level <= 3: log(message, 3)

def crit(message: str) -> None:
    if log_level <= 4: log(message, 4)