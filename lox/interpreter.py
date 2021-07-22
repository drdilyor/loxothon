from typing import Optional

import lox.expr as expr
import lox.lox as lox
import lox.stmt as stmt
from lox.environment import Environment
from lox.stmt import Block, R
from lox.token import TokenType as TT
from lox.error import LoxRuntimeError


class Interpreter(expr.Visitor[object], stmt.Visitor[None]):
    def __init__(self):
        self.environment = Environment()

    def interpret(self, statements: list[stmt.Stmt]) -> None:
        """Interprets expression and reports if runtime error occured"""
        try:
            for s in statements:
                self.execute(s)

        except LoxRuntimeError as e:
            lox.runtime_error(e)

    def interpret_expression(self, expression: expr.Expr) -> Optional[str]:
        """Evaluates expression and returns stringified value"""
        try:
            return self.stringify(self.evaluate(expression))
        except LoxRuntimeError as e:
            lox.runtime_error(e)
            return None

    def execute(self, s: stmt.Stmt) -> None:
        return s.accept(self)

    def execute_block(self, statements: list[stmt.Stmt], environment: Environment):
        previous = self.environment
        try:
            self.environment = environment
            for statement in statements:
                self.execute(statement)
        finally:
            self.environment = previous

    def visit_block_stmt(self, s: stmt.Block) -> None:
        self.execute_block(s.statements, Environment(self.environment))

    def visit_expression_stmt(self, s: stmt.Expression) -> None:
        self.evaluate(s.expression)

    def visit_print_stmt(self, s: stmt.Print) -> None:
        value = self.evaluate(s.expression)
        print(self.stringify(value))

    def visit_var_stmt(self, s: stmt.Var) -> None:
        self.environment.define(
            s.name.lexeme,
            self.evaluate(s.initializer) if s.initializer else None)

    def evaluate(self, expression: expr.Expr):
        return expression.accept(self)

    def visit_assign_expr(self, e: expr.Assign):
        self.environment.assign(e.name, value)

    def visit_binary_expr(self, e: expr.Binary):
        a, b = e.left.accept(self), e.right.accept(self)
        o = e.operator.type

        if o == TT.PLUS:
            try:
                return a + b
            except TypeError:
                raise LoxRuntimeError(
                    e.operator,
                    'Operands must be two numbers or two strings'
                )

        if o == TT.EQUAL_EQUAL:
            return a == b
        if o == TT.BANG_EQUAL:
            return a != b
        if o == TT.COMMA:
            return b

        # Number only expressions
        if not (isinstance(a, float) and isinstance(b, float)):
            raise LoxRuntimeError(e.operator, 'Operands must be numbers')

        if o == TT.MINUS:
            return a - b
        if o == TT.STAR:
            return a * b
        if o == TT.SLASH:
            try:
                return a / b
            except ZeroDivisionError:
                return float('nan')
        if o == TT.GREATER:
            return a > b
        if o == TT.GREATER_EQUAL:
            return a >= b
        if o == TT.LESS:
            return a < b
        if o == TT.LESS_EQUAL:
            return a <= b
        # unreachable

    def visit_conditional_expr(self, e: expr.Conditional):
        if self.is_truthy(e.condition.accept(self)):
            return e.then_branch.accept(self)
        else:
            return e.else_branch.accept(self)

    def visit_grouping_expr(self, e: expr.Grouping):
        return e.expression.accept(self)

    def visit_literal_expr(self, e: expr.Literal):
        return e.value

    def visit_unary_expr(self, e: expr.Unary):
        a = e.right.accept(self)
        o = e.operator.type
        if o == TT.BANG:
            return not self.is_truthy(a)
        if o == TT.MINUS:
            if not isinstance(a, float):
                raise LoxRuntimeError(e.operator, "Operand must be a number.")
            return -a
        # unreachable

    def visit_variable_expr(self, e: expr.Variable):
        return self.environment.get(e.name)

    def is_truthy(self, obj):
        if obj is None:
            return False
        if obj is False:
            return False
        return True

    def stringify(self, obj):
        if obj is None:
            return 'nil'
        if isinstance(obj, float):
            return format(obj, 'g')
        if isinstance(obj, bool):
            return ('false', 'true')[obj]
        return str(obj)


__all__ = ['Interpreter']
