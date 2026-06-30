import operator
from ast import Expression, BinOp, UnaryOp, Constant, USub, UAdd, parse, NodeVisitor
from datetime import datetime, timedelta

from lib.chat.context import Context
from lib.chat.rule import Rule
from lib.rule_registry import register


OP_MAP = {
    'Add': operator.add, 'Sub': operator.sub,
    'Mult': operator.mul, 'Div': operator.truediv,
    'Pow': operator.pow,
}

UNARY_MAP = {UAdd: operator.pos, USub: operator.neg}


class _SafeEval(NodeVisitor):
    def visit_Expression(self, node):
        return self.visit(node.body)

    def visit_Constant(self, node):
        if isinstance(node.value, (int, float)):
            return node.value
        raise ValueError('仅支持数字')

    def visit_UnaryOp(self, node):
        val = self.visit(node.operand)
        op_func = UNARY_MAP.get(type(node.op))
        if not op_func:
            raise ValueError('不支持的运算符')
        return op_func(val)

    def visit_BinOp(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)
        op_func = OP_MAP.get(type(node.op).__name__)
        if not op_func:
            raise ValueError('不支持的运算符')
        return op_func(left, right)

    def generic_visit(self, node):
        raise ValueError('不支持的表达式')


def safe_eval(expr: str):
    return _SafeEval().visit(parse(expr, mode='eval'))


def format_stack(n: int) -> str:
    stacks = n // 64
    remainder = n % 64
    return f'{stacks}x64 + {remainder}'


def format_fluid(n: int) -> str:
    stacks = n // 9216
    r1 = n % 9216
    ingots = r1 // 144
    remainder = r1 % 144
    return f'{stacks}x64x144 + {ingots}x144 + {remainder}'


def format_time_line(label: str, real_seconds: int, ticks: int) -> str:
    DD = real_seconds // 86400
    HH = (real_seconds % 86400) // 3600
    MM = (real_seconds % 3600) // 60
    SS = real_seconds % 60
    mc_days = ticks // 24000
    time_str = f'{DD:02d}:{HH:02d}:{MM:02d}:{SS:02d}'
    eta = (datetime.now() + timedelta(seconds=real_seconds)).strftime('%m-%d %H:%M')
    return f'§5{label}§r: §e{time_str} §d{ticks}tick§r §3{mc_days}MC日§r §9ETA: §e{eta}§r'


@register
class InGameCalc(Rule):
    def __init__(self):
        super().__init__('游戏内计算器')

    def check(self, context: Context) -> bool:
        return context.chat_session.is_mc_chat() and context.get_message().startswith('!!calc ')

    async def handle(self, context: Context) -> bool:
        expr = context.get_message()[6:].strip()

        if not expr:
            await context.send_message('用法: !!calc <算式>')
            return False

        try:
            result = safe_eval(expr)
        except Exception:
            await context.send_message('算式无效')
            return False

        result_int = int(result)
        await context.send_message(
            f'§6结果§r: {result_int} '
            f'§a组数§r: {format_stack(result_int)} '
            f'§b流体锭§r: {format_fluid(result_int)}\n'
            f'{format_time_line("作为tick", result_int // 20, result_int)}\n'
            f'{format_time_line("作为秒", result_int, result_int * 20)}'
        )
        return False
