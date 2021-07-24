from typing import Optional, Dict, List

import lox
import lox.expr as expr
import lox.stmt as stmt
from lox.token import TokenType as TT, Token


class Interpreter(expr.Visitor[object], stmt.Visitor[None]):
    def __init__(self):
        self.globals = lox.Environment()
        self.environment = self.globals
        self.environment.define('clock', lox.lox_clock)
        self.locals: Dict[expr.Expr, int] = {}

    def interpret(self, statements: List[stmt.Stmt]) -> None:
        """Interprets expression and reports if runtime error occured"""
        try:
            for s in statements:
                self.execute(s)

        except lox.LoxRuntimeError as e:
            lox.lox.runtime_error(e)

    def interpret_expression(self, expression: expr.Expr) -> Optional[str]:
        """Evaluates expression and returns stringified value"""
        try:
            return self.stringify(self.evaluate(expression))
        except lox.LoxRuntimeError as e:
            lox.lox.runtime_error(e)
            return None

    def execute(self, s: stmt.Stmt) -> None:
        return s.accept(self)

    def execute_block(self,
                      statements: List[stmt.Stmt],
                      environment: lox.Environment):
        previous = self.environment
        try:
            self.environment = environment
            for statement in statements:
                self.execute(statement)
        finally:
            self.environment = previous

    def resolve(self, e: expr.Expr, depth: int):
        self.locals[e] = depth

    def visit_break_stmt(self, s: stmt.Break) -> None:
        raise lox.LoxStopIteration()

    def visit_block_stmt(self, s: stmt.Block) -> None:
        self.execute_block(s.statements, lox.Environment(self.environment))

    def visit_class_stmt(self, s: stmt.Class) -> None:
        class_ = lox.LoxClass(s.name, {
            i.name.lexeme: lox.LoxFunction(
                i, self.environment, i.name.lexeme == 'init')
            for i in s.methods
        })
        self.environment.define(s.name.lexeme, class_)

    def visit_expression_stmt(self, s: stmt.Expression) -> None:
        self.evaluate(s.expression)

    def visit_function_stmt(self, s: stmt.Function) -> None:
        function = lox.LoxFunction(s, self.environment)
        self.environment.define(s.name.lexeme, function)

    def visit_if_stmt(self, s: stmt.If) -> None:
        if self.is_truthy(self.evaluate(s.condition)):
            self.execute(s.then_branch)
        elif s.else_branch:
            self.execute(s.else_branch)

    def visit_print_stmt(self, s: stmt.Print) -> None:
        value = self.evaluate(s.expression)
        print(self.stringify(value))

    def visit_return_stmt(self, s: stmt.Return) -> None:
        value = s.value and self.evaluate(s.value)
        raise lox.LoxReturn(value)

    def visit_while_stmt(self, s: stmt.While) -> None:
        while self.is_truthy(self.evaluate(s.condition)):
            try:
                self.execute(s.body)
            except lox.LoxStopIteration:
                break

    def visit_var_stmt(self, s: stmt.Var) -> None:
        self.environment.define(
            s.name.lexeme,
            self.evaluate(s.initializer) if s.initializer else None)

    def evaluate(self, expression: expr.Expr):
        return expression.accept(self)

    def visit_assign_expr(self, e: expr.Assign):
        value = self.evaluate(e.value)
        distance = self.locals.get(e)
        if distance is not None:
            return self.environment.assign_at(distance, e.name, value)
        else:
            return self.globals.assign(e.name, value)

    def visit_binary_expr(self, e: expr.Binary):
        a, b = e.left.accept(self), e.right.accept(self)
        o = e.operator.type

        if o == TT.PLUS:
            try:
                return a + b
            except TypeError:
                raise lox.LoxRuntimeError(
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
            raise lox.LoxRuntimeError(e.operator, 'Operands must be numbers')

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

    def visit_call_expr(self, e: expr.Call):
        callee = self.evaluate(e.callee)
        arguments = [self.evaluate(i) for i in e.arguments]

        if not isinstance(callee, lox.LoxCallable):
            raise lox.LoxRuntimeError(e.paren,
                                      'Can only call functions and classes.')
        function: lox.LoxCallable = callee
        if len(arguments) != function.arity():
            raise lox.LoxRuntimeError(
                e.paren,
                f'Expected {function.arity()} '
                f'arguments but got {len(arguments)}.')

        return function.call(self, arguments)

    def visit_conditional_expr(self, e: expr.Conditional):
        if self.is_truthy(self.evaluate(e.condition)):
            return e.then_branch.accept(self)
        else:
            return e.else_branch.accept(self)

    def visit_get_expr(self, e: expr.Get):
        instance: 'lox.LoxInstance' = e.object.accept(self)
        if isinstance(instance, lox.LoxInstance):
            return instance.get(e.name)
        lox.lox.error_token(e.name,
                            'Can only access properties on instances.')

    def visit_grouping_expr(self, e: expr.Grouping):
        return e.expression.accept(self)

    def visit_literal_expr(self, e: expr.Literal):
        return e.value

    def visit_logical_expr(self, e: expr.Logical):
        left = self.evaluate(e.left)
        if e.operator.type == TT.OR:
            if self.is_truthy(left):
                return left
        else:
            if not self.is_truthy(left):
                return left
        return self.evaluate(e.right)

    def visit_set_expr(self, e: expr.Set):
        instance = self.evaluate(e.object)
        if not isinstance(instance, lox.LoxInstance):
            lox.lox.error_token(
                e.name, 'Can only set properties on instances.')
        instance.set(e.name, self.evaluate(e.value))

    def visit_this_expr(self, e: expr.This):
        return self.look_up_variable(e.keyword, e)

    def visit_unary_expr(self, e: expr.Unary):
        a = e.right.accept(self)
        o = e.operator.type
        if o == TT.BANG:
            return not self.is_truthy(a)
        if o == TT.MINUS:
            if not isinstance(a, float):
                raise lox.LoxRuntimeError(
                    e.operator, "Operand must be a number.")
            return -a
        # unreachable

    def visit_variable_expr(self, e: expr.Variable):
        return self.look_up_variable(e.name, e)

    def look_up_variable(self, name: Token, e: expr.Expr):
        distance = self.locals.get(e)
        if distance is not None:
            return self.environment.get_at(distance, name.lexeme)
        else:
            return self.globals.get(name)

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
