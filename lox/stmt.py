"""AUTOGENERATED! DO NOT EDIT! Make changes to tool/generate_ast.py instead"""
from abc import ABC, abstractmethod
from typing import Any, Generic, List, Optional, TypeVar
from dataclasses import dataclass

from lox.token import Token
from lox.expr import Expr

T = TypeVar('T')

class Stmt:
    def accept(self, visitor: 'Visitor[T]') -> T: ...

@dataclass(eq=False, frozen=True)
class Block(Stmt):
    statements: List[Stmt]

    def accept(self, visitor: 'Visitor[T]') -> T:
        return visitor.visit_block_stmt(self)

@dataclass(eq=False, frozen=True)
class Break(Stmt):
    keyword: Token

    def accept(self, visitor: 'Visitor[T]') -> T:
        return visitor.visit_break_stmt(self)

@dataclass(eq=False, frozen=True)
class Class(Stmt):
    name: Token
    methods: List['Function']
    class_methods: List['Function']
    getters: List['Function']

    def accept(self, visitor: 'Visitor[T]') -> T:
        return visitor.visit_class_stmt(self)

@dataclass(eq=False, frozen=True)
class Expression(Stmt):
    expression: Expr

    def accept(self, visitor: 'Visitor[T]') -> T:
        return visitor.visit_expression_stmt(self)

@dataclass(eq=False, frozen=True)
class Function(Stmt):
    name: Token
    params: List[Token]
    body: List[Stmt]

    def accept(self, visitor: 'Visitor[T]') -> T:
        return visitor.visit_function_stmt(self)

@dataclass(eq=False, frozen=True)
class If(Stmt):
    condition: Expr
    then_branch: Stmt
    else_branch: Stmt

    def accept(self, visitor: 'Visitor[T]') -> T:
        return visitor.visit_if_stmt(self)

@dataclass(eq=False, frozen=True)
class Print(Stmt):
    expression: Expr

    def accept(self, visitor: 'Visitor[T]') -> T:
        return visitor.visit_print_stmt(self)

@dataclass(eq=False, frozen=True)
class Return(Stmt):
    keyword: Token
    value: Expr

    def accept(self, visitor: 'Visitor[T]') -> T:
        return visitor.visit_return_stmt(self)

@dataclass(eq=False, frozen=True)
class Var(Stmt):
    name: Token
    initializer: Optional[Expr]

    def accept(self, visitor: 'Visitor[T]') -> T:
        return visitor.visit_var_stmt(self)

@dataclass(eq=False, frozen=True)
class While(Stmt):
    condition: Expr
    body: Stmt

    def accept(self, visitor: 'Visitor[T]') -> T:
        return visitor.visit_while_stmt(self)

R = TypeVar('R')

class Visitor(Generic[R], ABC):
    @abstractmethod
    def visit_block_stmt(self, s: Block) -> R: ...
    @abstractmethod
    def visit_break_stmt(self, s: Break) -> R: ...
    @abstractmethod
    def visit_class_stmt(self, s: Class) -> R: ...
    @abstractmethod
    def visit_expression_stmt(self, s: Expression) -> R: ...
    @abstractmethod
    def visit_function_stmt(self, s: Function) -> R: ...
    @abstractmethod
    def visit_if_stmt(self, s: If) -> R: ...
    @abstractmethod
    def visit_print_stmt(self, s: Print) -> R: ...
    @abstractmethod
    def visit_return_stmt(self, s: Return) -> R: ...
    @abstractmethod
    def visit_var_stmt(self, s: Var) -> R: ...
    @abstractmethod
    def visit_while_stmt(self, s: While) -> R: ...
