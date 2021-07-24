from enum import Enum
from typing import List, Dict, Union

import lox
import lox.expr as expr
import lox.stmt as stmt
# from lox import lox
# from lox.token import Token
# from lox.interpreter import *  # for type checks only


class _ResolverMakeScope:
    def __init__(self, resolver: 'Resolver'):
        self.resolver = resolver

    def __enter__(self):
        self.resolver.begin_scope()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.resolver.end_scope()


class FunctionType(Enum):
    NONE = 0
    FUNCTION = 1


class VarState:
    def __init__(self, name: 'lox.Token'):
        self.name = name
        self.defined = False
        self.used = False


class Resolver(expr.Visitor[None], stmt.Visitor[None]):
    def __init__(self, interpreter: 'lox.Interpreter'):
        self.interpreter = interpreter
        self.scopes: List[Dict[str, VarState]] = []
        self.current_function = FunctionType.NONE
        self.loop_depth = 0

    def resolve(self, obj: Union[List[stmt.Stmt], stmt.Stmt, expr.Expr]):
        if isinstance(obj, list):
            for i in obj:
                i.accept(self)
        else:
            obj.accept(self)

    def resolve_local(self, e: expr.Expr, name: 'lox.Token', used=True):
        i = len(self.scopes) - 1
        while i >= 0:
            if name.lexeme in self.scopes[i]:
                self.interpreter.resolve(e, len(self.scopes) - 1 - i)
                if used:
                    self.scopes[i][name.lexeme].used = True
                break
            i -= 1

    def resolve_function(self, function: stmt.Function, type: FunctionType):
        enclosing_function = self.current_function
        self.current_function = type
        previous_loop_depth = self.loop_depth
        self.loop_depth = 0
        with self.make_scope():
            for param in function.params:
                self.declare(param)
                self.define(param)
            self.resolve(function.body)
        self.current_function = enclosing_function
        self.loop_depth = previous_loop_depth

    def begin_scope(self):
        self.scopes.append({})

    def end_scope(self):
        for name, var_state in self.scopes.pop().items():
            if not var_state.used:
                lox.lox.error_token(
                    var_state.name, f"Unused local variable '{name}'.")

    def make_scope(self):
        return _ResolverMakeScope(self)

    def declare(self, name: 'lox.Token'):
        if self.scopes:
            if name.lexeme in self.scopes[-1]:
                lox.lox.error_token(
                    name, 'Already a variable with this name in this scope.')
            self.scopes[-1][name.lexeme] = VarState(name)

    def define(self, name: 'lox.Token'):
        if self.scopes:
            self.scopes[-1][name.lexeme].defined = True

    def visit_block_stmt(self, s: stmt.Block) -> None:
        with self.make_scope():
            self.resolve(s.statements)

    def visit_break_stmt(self, s: stmt.Break) -> None:
        if not self.loop_depth:
            lox.lox.error_token(s.keyword, "Break outside a loop.")

    def visit_expression_stmt(self, s: stmt.Expression) -> None:
        self.resolve(s.expression)

    def visit_function_stmt(self, s: stmt.Function) -> None:
        self.declare(s.name)
        self.define(s.name)
        self.resolve_function(s, FunctionType.FUNCTION)

    def visit_if_stmt(self, s: stmt.If) -> None:
        self.resolve(s.condition)
        self.resolve(s.then_branch)
        if s.else_branch:
            self.resolve(s.else_branch)

    def visit_print_stmt(self, s: stmt.Print) -> None:
        self.resolve(s.expression)

    def visit_return_stmt(self, s: stmt.Return) -> None:
        if self.current_function == FunctionType.NONE:
            lox.lox.error_token(s.keyword, "Can't return from top-level code.")
        if s.value:
            self.resolve(s.value)

    def visit_var_stmt(self, s: stmt.Var) -> None:
        self.declare(s.name)
        if s.initializer:
            self.resolve(s.initializer)
        self.define(s.name)

    def visit_while_stmt(self, s: stmt.While) -> None:
        self.loop_depth += 1
        self.resolve(s.condition)
        self.resolve(s.body)
        self.loop_depth -= 1

    def visit_assign_expr(self, e: expr.Assign) -> None:
        self.resolve(e.value)
        self.resolve_local(e, e.name, False)

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
        if self.scopes:
            state = self.scopes[-1].get(e.name.lexeme)
            if state and not state.defined:
                message = "Can't read local variable in its own initializer."
                lox.lox.error_token(e.name, message)

        self.resolve_local(e, e.name)


__all__ = ['Resolver']
