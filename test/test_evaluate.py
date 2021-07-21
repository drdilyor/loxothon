import pytest

from lox import Interpreter, Parser, Scanner, LoxRuntimeError
from lox import lox


# this assumes scanner and parser don't have bugs
def evaluate(s):
    return Interpreter().evaluate(Parser(Scanner(s).scan_tokens()).parse())


@pytest.mark.parametrize('s,expected', [
    ('3 + 3 * -3', -6),
    ('3 / 3 - 1', 0),
    ('"hello" + " world"', 'hello world'),
    ('!true', False),
    ('1 == 5', False),
    ('1 != 5', True),
    ('1 > 5', False),
    ('1 < 5', True),
    ('1 >= 1', True),
    ('1 <= 1', True),
    ('true ? 1 : 2', 1),
    ('false ? 1 : 2', 2),
    ('1, 2', 2),
    ('(2 + 1) * 2', 6),
    ('!!nil', False),
    ('!!0', True),
])
def test_expressions(s, expected):
    assert evaluate(s) == expected


def test_divide_by_zero():
    value = evaluate('42 / 0')
    assert isinstance(value, float)
    assert value != value # only nan doesn't equal to itself!


def code(source: str) -> list[str]:
    return list(filter(bool, map(str.strip, source.strip().split('\n'))))


@pytest.mark.parametrize('s', code("""
    -"muffin"
    nil + nil
    "3" - 1
"""))
def test_errors(s):
    with pytest.raises(LoxRuntimeError):
        assert evaluate(s) is None

@pytest.mark.parametrize('s,expected', [
    ('nil', 'nil'),
    ('0', '0'),
    ('0.0', '0'),
    ('999.99', '999.99'),
    ('"string"', 'string'),
    ('true', 'true'),  # No capital letters!
    ('false', 'false'),
])
def test_interpret_method(s, expected, capsys):
    # Note that stringify is private api

    Interpreter().interpret(Parser(Scanner(s).scan_tokens()).parse())
    assert capsys.readouterr().out == expected + '\n'


def test_interpret_method_error(capsys):
    s = '-"muffin"'
    Interpreter().interpret(Parser(Scanner(s).scan_tokens()).parse())
    assert 'line' in capsys.readouterr().out
    assert lox.had_runtime_error

