from os.path import dirname, abspath, join
import sys
from typing import Dict, List, Tuple


def define_ast(file, base: str, ast: Dict[str, List[str]], imports: List[Tuple[str, str]] = []):  # noqa
    print(end=f'pouring ast into {file}... ')
    sys.stdout.flush()

    f = open(join(dirname(dirname(abspath(__file__))), 'lox', file), 'w+')
    f.write('"""AUTOGENERATED! DO NOT EDIT! Make changes to tool/generate_ast.py instead"""\n')
    f.write('from abc import ABC, abstractmethod\n')
    f.write('from typing import Any, Generic, List, Optional, TypeVar\n')
    f.write('from collections import namedtuple')
    f.write('\n')

    if imports:
        for p, i in imports:
            f.write(f'from lox.{p} import {i}\n')
        f.write('\n')

    f.write(f"T = TypeVar('T')\n")
    f.write(f'\n')
    f.write(f"class {base}:\n")
    f.write(f"    def accept(self, visitor: 'Visitor[T]') -> T: ...\n")
    f.write(f'    def __hash__(self): return id(self)\n')
    f.write(f'\n')

    for cls, fields in ast.items():
        args = ' '.join(i.partition(':')[0].strip() for i in fields)
        f.write(f"class {cls}({base}, namedtuple('{cls}', '{args}')):\n")
        f.write(f"    def accept(self, visitor: 'Visitor[T]') -> T:\n")
        f.write(f"        return visitor.visit_{cls.lower()}_{base.lower()}(self)\n")
        f.write('\n')

    f.write(f"R = TypeVar('R')\n")
    f.write('\n')
    f.write(f"class Visitor(Generic[R], ABC):\n")

    for cls in ast:
        f.write(f'    @abstractmethod\n')
        f.write(f"    def visit_{cls.lower()}_{base.lower()}(self, {base[0].lower()}: {cls}) -> R: ...\n")
    print('done')


define_ast('expr.py', 'Expr', {
    'Assign': ['name: Token', 'value: Expr'],
    'Binary': ['left: Expr', 'operator: Token', 'right: Expr'],
    'Call': ['callee: Expr', 'paren: Token', 'arguments: List[Expr]'],
    'Conditional': ['condition: Expr', 'then_branch: Expr', 'else_branch: Expr'],
    'Get': ['object: Expr', 'name: Token'],
    'Grouping': ['expression: Expr'],
    'Literal': ['value: Any'],
    'Logical': ['left: Expr', 'operator: Token', 'right: Expr'],
    'Set': ['object: Expr', 'name: Token', 'value: Expr'],
    'This': ['keyword: Token'],
    'Unary': ['operator: Token', 'right: Expr'],
    'Variable': ['name: Token'],
}, imports=[
    ('token', 'Token'),
])

define_ast('stmt.py', 'Stmt', {
    'Block': ['statements: List[Stmt]'],
    'Break': ['keyword: Token'],
    'Class': [
        'name: Token',
        "methods: List['Function']",
        "setters: List['Function']",
        "class_methods: List['Function']",
        "class_setters: List['Function']",
    ],
    'Expression': ['expression: Expr'],
    'Function': [
        'name: Token',
        'params: List[Token]',
        'body: List[Stmt]',
        'is_getter: bool',
        'is_setter: bool',
    ],
    'If': ['condition: Expr', 'then_branch: Stmt', 'else_branch: Stmt'],
    'Print': ['expression: Expr'],
    'Return': ['keyword: Token', 'value: Expr'],
    'Var': ['name: Token', 'initializer: Optional[Expr]'],
    'While': ['condition: Expr', 'body: Stmt'],
}, imports=[
    ('token', 'Token'),
    ('expr', 'Expr'),
])
