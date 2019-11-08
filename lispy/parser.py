from lark import Lark, InlineTransformer
from pathlib import Path

from .runtime import Symbol


class LispTransformer(InlineTransformer):
    number = float

    def start(self, *args):
        return [Symbol.BEGIN, *args]

    def string(self,  string):
        return str(string[1:-1]).replace('\\n', '\n')\
            .replace('\\t', '\t')\
            .replace('\\f', '\f')\
            .replace('\\r', '\r')\
            .replace('\\"', '\"')

    def op(self, op):
        return Symbol(op)

    def name(self, name):
        return Symbol(name)

    def bool(self, value):
        return True if value == "#t" else False

    def list(self, *args):
        return list(args)

    def quote(self, expr):
        return [Symbol.QUOTE, expr]

    def infix(self, x, op, y):
        if isinstance(x, list) or isinstance(y, list):
            return [[Symbol(op)], x, y]
        return [Symbol(op), x, y]

    def assign(self, name, expr):
        return [Symbol(name), expr]

    def sugar_let(self, *args):
        *assigns, expr = args
        return [Symbol.LET, assigns, expr]

    def eliff(self, cond, true):
        return [cond, true]

    def sugar_if(self, *args):
        cond, true, *elifs, false = args
        if not elifs:
            return [Symbol.IF, cond, true, false]
        return [Symbol.IF, cond, true,
                self.sugar_if(*elifs[0], *elifs[1:], false)]

    def sugar_fn(self, *args):
        *params, body = args
        return ['fn', params, body]

    def function(self, *args):
        name, *params, body = args
        return ['defn', str(name), params, body]

    def lists(self, *args):
        return [Symbol.LIST] + list(args)


def parse(src: str):
    """
    Compila string de entrada e retorna a S-expression equivalente.
    """
    return parser.parse(src)


def _make_grammar():
    """
    Retorna uma gramática do Lark inicializada.
    """

    path = Path(__file__).parent / 'grammar.lark'
    with open(path) as fd:
        grammar = Lark(fd, parser='lalr', transformer=LispTransformer())
    return grammar

parser = _make_grammar()
