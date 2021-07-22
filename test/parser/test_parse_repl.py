from lox import expr, Parser, Scanner


def parse(s):
    return Parser(Scanner(s).scan_tokens()).parse_repl()


def test_expression():
    assert isinstance(parse('3 + 1'), expr.Expr)


def test_statement():
    assert isinstance(parse('var answer = 42;'), list)
    assert isinstance(parse('3 + 1;'), list)
