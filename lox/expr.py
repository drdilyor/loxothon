"""AUTOGENERATED! DO NOT EDIT! Make changes to tool/generate_ast.py instead"""
from abc import ABC, abstractmethod
from typing import Any, Generic, Optional, TypeVar
from dataclasses import dataclass

from lox.token import Token

T = TypeVar('T')

class Expr:
    def accept(self, visitor: 'Visitor[T]') -> T: ...

@dataclass
class Assign(Expr):
    name: Token
    value: Expr

    def accept(self, visitor: 'Visitor[T]') -> T:
        return visitor.visit_assign_expr(self)

@dataclass
class Binary(Expr):
    left: Expr
    operator: Token
    right: Expr

    def accept(self, visitor: 'Visitor[T]') -> T:
        return visitor.visit_binary_expr(self)

@dataclass
class Conditional(Expr):
    condition: Expr
    then_branch: Expr
    else_branch: Expr

    def accept(self, visitor: 'Visitor[T]') -> T:
        return visitor.visit_conditional_expr(self)

@dataclass
class Grouping(Expr):
    expression: Expr

    def accept(self, visitor: 'Visitor[T]') -> T:
        return visitor.visit_grouping_expr(self)

@dataclass
class Literal(Expr):
    value: Any

    def accept(self, visitor: 'Visitor[T]') -> T:
        return visitor.visit_literal_expr(self)

@dataclass
class Unary(Expr):
    operator: Token
    right: Expr

    def accept(self, visitor: 'Visitor[T]') -> T:
        return visitor.visit_unary_expr(self)

@dataclass
class Variable(Expr):
    name: Token

    def accept(self, visitor: 'Visitor[T]') -> T:
        return visitor.visit_variable_expr(self)

R = TypeVar('R')

class Visitor(Generic[R], ABC):
    @abstractmethod
    def visit_assign_expr(self, e: Assign) -> R: ...
    @abstractmethod
    def visit_binary_expr(self, e: Binary) -> R: ...
    @abstractmethod
    def visit_conditional_expr(self, e: Conditional) -> R: ...
    @abstractmethod
    def visit_grouping_expr(self, e: Grouping) -> R: ...
    @abstractmethod
    def visit_literal_expr(self, e: Literal) -> R: ...
    @abstractmethod
    def visit_unary_expr(self, e: Unary) -> R: ...
    @abstractmethod
    def visit_variable_expr(self, e: Variable) -> R: ...
