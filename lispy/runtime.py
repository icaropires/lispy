import math
import operator as op
from collections import ChainMap
from types import MappingProxyType

from .symbol import Symbol


def eval(x, env=None):
    """
    Avalia expressão no ambiente de execução dado.
    """
    # Cria ambiente padrão, caso o usuário não passe o argumento opcional "env"
    if env is None:
        env = ChainMap({}, global_env)

    # Avalia tipos atômicos
    if isinstance(x, Symbol):
        return env[x]
    elif isinstance(x, (int, float, bool, str)):
        return x
    # Avalia formas especiais e listas
    head, *args = x

    if isinstance(head, (int, float, bool)):
        return x

    # Comando (if <test> <then> <other>)
    # Ex: (if (even? x) (quotient x 2) x)
    if head == Symbol.IF:
        (test, then, alt) = args
        return eval(then, env) if eval(test, env) else eval(alt, env)

    # Comando (define <symbol> <expression>)
    # Ex: (define x (+ 40 2))
    elif head == Symbol.DEFINE:
        symbol, exp = args
        env[symbol] = eval(exp, env)

    # Comando (quote <expression>)
    # (quote (1 2 3))
    elif head == Symbol.QUOTE:
        return x[1]

    # Comando (let <expression> <expression>)
    # (let ((x 1) (y 2)) (+ x y))
    elif head == Symbol.LET:
        local, expr = args

        tmp_env = env.copy()
        for k,v in local:
            tmp_env[k] = eval(v, tmp_env)

        return eval(expr, tmp_env)

    # Comando (lambda <vars> <body>)
    # (lambda (x) (+ x 1))
    elif head == Symbol.LAMBDA or head == Symbol.FN:
        params, body = args

        if not isinstance(params, list):
            params = [params]

        if not all(map(lambda a: isinstance(a, Symbol), params)):
            raise TypeError('Invalid params on lambda definition!')

        def lambdaa(*args):
            local = env.new_child(
                {Symbol(k): eval(v, env) for k, v in zip(params, args)}
            )
            return eval(body, local)

        return lambdaa

    elif head == Symbol.DEFN:
        name, params, body = args

        if not all(map(lambda a: isinstance(a, Symbol), params)):
            raise TypeError('Invalid params on lambda definition!')

        def fn(*args):
            local = env.new_child(
                {Symbol(k): eval(v, env) for k, v in zip(params, args)}
            )
            return eval(body, local)

        env[Symbol(name)] = fn

    elif head == Symbol.LIST:
        result = Symbol.LIST
        for l in args:
            result = eval(l, env)
        return [result]

    # Lista/chamada de funções
    # (sqrt 4)
    else:
        args = map(eval, args, [env]*len(args))
        args = list(args)
        return env[head](*args)


#
# Cria ambiente de execução.
#
def env(*args, **kwargs):
    """
    Retorna um ambiente de execução que pode ser aproveitado pela função
    eval().

    Aceita um dicionário como argumento posicional opcional. Argumentos nomeados
    são salvos como atribuições de variáveis.

    Ambiente padrão
    >>> env()
    {...}

    Acrescenta algumas variáveis explicitamente
    >>> env(x=1, y=2)
    {x: 1, y: 2, ...}

    Passa um dicionário com variáveis adicionais
    >>> d = {Symbol('x'): 1, Symbol('y'): 2}
    >>> env(d)
    {x: 1, y: 2, ...}
    """

    kwargs = {Symbol(k): v for k, v in kwargs.items()}
    if len(args) > 1:
        raise TypeError('accepts zero or one positional arguments')
    elif len(args):
        if any(not isinstance(x, Symbol) for x in args[0]):
            raise ValueError('keys in a environment must be Symbols')
        args[0].update(kwargs)
        return ChainMap(args[0], global_env)
    return ChainMap(kwargs, global_env)


def _make_global_env():
    """
    Retorna dicionário fechado para escrita relacionando o nome das variáveis aos
    respectivos valores.
    """

    dic = {
        **vars(math), # sin, cos, sqrt, pi, ...
        '+':op.add, '-':op.sub, '*':op.mul, '/':op.truediv,
        '>':op.gt, '<':op.lt, '>=':op.ge, '<=':op.le, '=':op.eq,
        'abs':     abs,
        'append':  op.add,
        'apply':   lambda proc, args: proc(*args),
        'begin':   lambda *x: x[-1],
        'car':     lambda x: head,
        'cdr':     lambda x: x[1:],
        'cons':    lambda x,y: [x] + y,
        'eq?':     op.is_,
        'expt':    pow,
        'equal?':  op.eq,
        'even?':   lambda x: x % 2 == 0,
        'length':  len,
        'list':    lambda *x: list(x),
        'list?':   lambda x: isinstance(x, list),
        'map':     map,
        'max':     max,
        'min':     min,
        'not':     op.not_,
        'null?':   lambda x: x == [],
        'number?': lambda x: isinstance(x, (float, int)),
        'odd?':   lambda x: x % 2 == 1,
        'print':   print,
        'procedure?': callable,
        'quotient': op.floordiv,
        'round':   round,
        'symbol?': lambda x: isinstance(x, Symbol),
    }
    return MappingProxyType({Symbol(k): v for k, v in dic.items()})

global_env = _make_global_env()
