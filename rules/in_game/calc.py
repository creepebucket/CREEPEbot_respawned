import operator
from ast import Expression, BinOp, UnaryOp, Constant, USub, UAdd, parse, NodeVisitor

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
    ingots = n // 144
    remainder = n % 144
    return f'{ingots}x144 + {remainder}'


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
            f'结果: {result_int} '
            f'组数: {format_stack(result_int)} '
            f'流体锭: {format_fluid(result_int)}'
        )
        return False
