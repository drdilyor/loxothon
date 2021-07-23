from typing import Union

import lox.expr as expr
import lox.stmt as stmt
from lox import lox
from lox.token import Token
from lox.interpreter import *  # for type checks only


class _ResolverMakeScope:
    def __init__(self, resolver: 'Resolver'):
        self.resolver = resolver

    def __enter__(self):
        self.resolver.scopes.append({})

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.resolver.scopes.pop()


class Resolver(expr.Visitor[None], stmt.Visitor[None]):
    def __init__(self, interpreter: Interpreter):
        self.interpreter = interpreter
        self.scopes: list[dict[str, bool]] = []

    def resolve(self, obj: Union[list[stmt.Stmt], stmt.Stmt, expr.Expr]):
        if isinstance(obj, list):
            for i in obj:
                i.accept(self)
        else:
            obj.accept(self)

    def resolve_local(self, e: expr.Expr, name: Token):
        i = len(self.scopes) - 1
        while i >= 0:
            if name.lexeme in self.scopes[i]:
                self.interpreter.resolve(e, len(self.scopes) - 1 - i)
                break
            i -= 1

    def resolve_function(self, function: stmt.Function):
        with self.make_scope():
            for param in function.params:
                self.declare(param)
                self.define(param)
            self.resolve(function.body)

    def make_scope(self):
        return _ResolverMakeScope(self)

    def declare(self, name: Token):
        if self.scopes:
            self.scopes[-1][name.lexeme] = False

    def define(self, name: Token):
        if self.scopes:
            self.scopes[-1][name.lexeme] = True

    def visit_block_stmt(self, s: stmt.Block) -> None:
        with self.make_scope():
            self.resolve(s.statements)

    def visit_break_stmt(self, s: stmt.Break) -> None:
        pass

    def visit_expression_stmt(self, s: stmt.Expression) -> None:
        self.resolve(s.expression)

    def visit_function_stmt(self, s: stmt.Function) -> None:
        self.declare(s.name)
        self.define(s.name)
        self.resolve_function(s)

    def visit_if_stmt(self, s: stmt.If) -> None:
        self.resolve(s.condition)
        self.resolve(s.then_branch)
        if s.else_branch:
            self.resolve(s.else_branch)

    def visit_print_stmt(self, s: stmt.Print) -> None:
        self.resolve(s.expression)

    def visit_return_stmt(self, s: stmt.Return) -> None:
        self.resolve(s.value)

    def visit_var_stmt(self, s: stmt.Var) -> None:
        self.declare(s.name)
        if s.initializer:
            self.resolve(s.initializer)
        self.define(s.name)

    def visit_while_stmt(self, s: stmt.While) -> None:
        self.resolve(s.condition)
        self.resolve(s.body)

    def visit_assign_expr(self, e: expr.Assign) -> None:
        self.resolve(e.value)
        self.resolve_local(e, e.name)

    def visit_binary_expr(self, e: expr.Binary) -> None:
        self.resolve(e.left)
        self.resolve(e.right)

    def visit_call_expr(self, e: expr.Call) -> None:
        self.resolve(e.callee)
        for arg in e.arguments:
            self.resolve(arg)

    def visit_conditional_expr(self, e: expr.Conditional) -> None:
        self.resolve(e.condition)
        self.resolve(e.else_branch)
        self.resolve(e.then_branch)

    def visit_grouping_expr(self, e: expr.Grouping) -> None:
        self.resolve(e.expression)

    def visit_literal_expr(self, e: expr.Literal) -> None:
        pass

    def visit_logical_expr(self, e: expr.Logical) -> None:
        self.resolve(e.left)
        self.resolve(e.right)

    def visit_unary_expr(self, e: expr.Unary) -> None:
        self.resolve(e.right)

    def visit_variable_expr(self, e: expr.Variable) -> None:
        if self.scopes and self.scopes[-1].get(e.name.lexeme) is False:
            lox.error_token(e.name, "Can't read local variable in its own initializer.")

        self.resolve_local(e, e.name)


__all__ = ['Resolver']
