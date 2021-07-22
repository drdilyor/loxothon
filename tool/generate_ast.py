import sys
from os.path import dirname, abspath, join


def define_ast(file, base: str, ast: dict[str, list[str]], imports: list[tuple[str, str]] = []):  # noqa
    print(end=f'pouring ast into {file}... ')
    sys.stdout.flush()

    f = open(join(dirname(dirname(abspath(__file__))), 'lox', file), 'w+')
    f.write('"""AUTOGENERATED! DO NOT EDIT! Make changes to tool/generate_ast.py instead"""\n')
    f.write('from abc import ABC, abstractmethod\n')
    f.write('from typing import Any, Generic, Optional, TypeVar\n')
    f.write('from dataclasses import dataclass\n')
    f.write('\n')

    if imports:
        for p, i in imports:
            f.write(f'from lox.{p} import {i}\n')
        f.write('\n')

    f.write(f"T = TypeVar('T')\n")
    f.write(f'\n')
    f.write(f"class {base}:\n")
    f.write(f"    def accept(self, visitor: 'Visitor[T]') -> T: ...\n")
    f.write(f'\n')

    for cls, fields in ast.items():
        f.write(f'@dataclass\n')
        f.write(f'class {cls}({base}):\n')
        for field in fields or ['pass']:
            f.write(f'    {field}\n')
        f.write('\n')
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
    'Conditional': ['condition: Expr', 'then_branch: Expr', 'else_branch: Expr'],
    'Grouping': ['expression: Expr'],
    'Literal': ['value: Any'],
    'Logical': ['left: Expr', 'operator: Token', 'right: Expr'],
    'Unary': ['operator: Token', 'right: Expr'],
    'Variable': ['name: Token'],
}, imports=[
    ('token', 'Token'),
])

define_ast('stmt.py', 'Stmt', {
    'Block': ['statements: list[Stmt]'],
    'Break': [],
    'Expression': ['expression: Expr'],
    'If': ['condition: Expr', 'then_branch: Stmt', 'else_branch: Stmt'],
    'Print': ['expression: Expr'],
    'Var': ['name: Token', 'initializer: Optional[Expr]'],
    'While': ['condition: Expr', 'body: Stmt'],
}, imports=[
    ('token', 'Token'),
    ('expr', 'Expr'),
])
