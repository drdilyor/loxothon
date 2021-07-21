import lox.expr as expr
import lox.lox as lox
from lox.token import Token, TokenType as TT


class LoxRuntimeError(Exception):
    def __init__(self, token: Token, message: str):
        self.token = token
        self.message = message
        super().__init__(message)


class Interpreter(expr.Visitor):
    def interpret(self, expression: expr.Expr):
        """Interprets expression and reports if runtime error occured"""
        try:
            value = self.evaluate(expression)
            print(self.stringify(value))
        except LoxRuntimeError as e:
            lox.runtime_error(e)

    def evaluate(self, expression):
        return expression.accept(self)

    def visitBinaryExpr(self, e: expr.Binary):
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

    def visitConditionalExpr(self, e: expr.Conditional):
        if self.is_truthy(e.condition.accept(self)):
            return e.then_branch.accept(self)
        else:
            return e.else_branch.accept(self)

    def visitGroupingExpr(self, e: expr.Grouping):
        return e.expression.accept(self)

    def visitLiteralExpr(self, e: expr.Literal):
        return e.value

    def visitUnaryExpr(self, e: expr.Unary):
        a = e.right.accept(self)
        o = e.operator.type
        if o == TT.BANG:
            return not self.is_truthy(a)
        if o == TT.MINUS:
            if not isinstance(a, float):
                raise LoxRuntimeError(e.operator, "Operand must be a number.")
            return -a
        # unreachable

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


__all__ = ['Interpreter', 'LoxRuntimeError']
