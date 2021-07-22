from lox import Interpreter, Parser, Scanner
from lox import lox


def interpert(s):
    return Interpreter().interpret_expression(Parser(Scanner(s).scan_tokens()).expression())

def test_intperpret_expression():
    assert interpert('3 + 3') == '6'
    assert interpert('nil') == 'nil'


def test_intperpret_expression_fail():
    assert interpert('nil + nil') is None
    assert lox.had_runtime_error
