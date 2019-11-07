from lark import Lark, InlineTransformer
from pathlib import Path
import re

from .runtime import Symbol


class LispTransformer(InlineTransformer):
    number = float 

    def start(self, *args):
        return [Symbol.BEGIN, *args]

    def string(self,  string):
        return str(string[1:-1]).replace('\\n', '\n').replace('\\t', '\t').replace('\\f', '\f').replace('\\r', '\r').replace('\\"', '\"')

    def op(self, op):
        return Symbol(op)

    def name(self, name):
        return Symbol(name)

    def bool(self, value):
        return True if value == "#t" else False

    def binop(self, op, left, right):
        op = str(op)
        return [Symbol(op), left, right]

    def list(self, *args):
        return list(args)

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
