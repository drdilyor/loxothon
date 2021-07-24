from lox import Interpreter, Parser, Resolver, Scanner
from lox import lox


def interpert(s):
    interpreter = Interpreter()
    statements = Parser(Scanner(s).scan_tokens()).expression()
    Resolver(interpreter).resolve(statements)
    return interpreter.interpret_expression(statements)


def test_intperpret_expression():
    assert interpert('3 + 3') == '6'
    assert interpert('nil') == 'nil'


def test_intperpret_expression_fail():
    assert interpert('nil + nil') is None
    assert lox.had_runtime_error
