from lox.expr import *
from lox.stmt import *
from lox.token import Token as T, TokenType as TT
from lox.printer import AstPrinter

def test_printer():
    assert AstPrinter().print([
        Print(
            Binary(
                Unary(
                    T(TT.MINUS, '-', None, 1),
                    Literal(123)),
                T(TT.STAR, '*', None, 1),
                Grouping(
                    Conditional(
                        Literal(True),
                        Literal(42),
                        Literal(0))))),
        Expression(
            Literal(123))
    ]) == '(print (* (- 123) (group (?: True 42 0))))\n(expression 123)'
