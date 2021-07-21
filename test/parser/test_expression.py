import pytest
from lox import expr, Parser, Scanner, TokenType as TT  # noqa
import lox.lox as lox

scan = lambda s: Scanner(s).scan_tokens()  # noqa
# note that expression is private api
parse = lambda s: Parser(scan(s)).expression()  # noqa

@pytest.fixture(autouse=True)
def set_had_error_false():
    try:
        yield
    finally:
        lox.had_error = False


@pytest.mark.parametrize('s', ['true', 'false', 'nil', '1', '99.99' '"string"'])
def test_primary(s):
    e = parse(s)
    assert isinstance(e, expr.Literal)


@pytest.mark.parametrize('s', ['-1', '!1'])
def test_unary(s):
    e = parse(s)
    assert isinstance(e, expr.Unary)
    assert isinstance(e.right, expr.Literal)


def test_unary_chain():
    e = parse('!-!-1')
    assert isinstance(e, expr.Unary)
    assert isinstance(e.right, expr.Unary)
    assert isinstance(e.right.right, expr.Unary)
    assert isinstance(e.right.right.right, expr.Unary)
    assert isinstance(e.right.right.right.right, expr.Literal)


def assert_binary_literal(e: expr.Expr):
    assert isinstance(e, expr.Binary)
    assert isinstance(e.left, expr.Literal)
    assert isinstance(e.right, expr.Literal)


@pytest.mark.parametrize('s,tt', [
    ('3 * 4', TT.STAR),
    ('3 / 4', TT.SLASH),
    ('3 + 4', TT.PLUS),
    ('3 - 4', TT.MINUS),
    ('3 > 4', TT.GREATER),
    ('3 < 4', TT.LESS),
    ('3 >= 4', TT.GREATER_EQUAL),
    ('3 <= 4', TT.LESS_EQUAL),
    ('3 == 4', TT.EQUAL_EQUAL),
    ('3 != 4', TT.BANG_EQUAL),
    ('3, 4', TT.COMMA)
])
def test_binary(s, tt):
    e = parse(s)
    assert_binary_literal(e)
    assert e.operator.type == tt


@pytest.mark.parametrize('s,tt2,tt1', [
    ('3 * 3 / 9', TT.SLASH, TT.STAR),
    ('3 + 3 - 9', TT.MINUS, TT.PLUS),
    ('3 > 2 < 4', TT.LESS, TT.GREATER),
    ('3 >= 2 <= 4', TT.LESS_EQUAL, TT.GREATER_EQUAL),
    ('3 != 2 == 4', TT.EQUAL_EQUAL, TT.BANG_EQUAL),
])
def test_double_binary_chain(s, tt2, tt1):
    e = parse(s)
    assert isinstance(e, expr.Binary)
    assert e.operator.type == tt2
    assert_binary_literal(e.left)
    assert e.left.operator.type == tt1


def test_grouping():
    e = parse('(3)')
    assert isinstance(e, expr.Grouping)
    assert isinstance(e.expression, expr.Literal)
    e = parse('(3,42)')
    assert isinstance(e, expr.Grouping)
    assert isinstance(e.expression, expr.Binary)


@pytest.mark.parametrize('s', [
    '+ -',
    '/ * /',
    '+ * * ! == <= >= !=',
    '3 * * 3',
    '* 3 3 *',
    '* 3',
    '3 +',
    '/ 3 *',
    '== 3 3',
])
def test_binary_error(s):
    assert parse(s) == None
    assert lox.had_error


@pytest.mark.parametrize('s', [
    '(42',
    '(42 (3)',
])
def test_grouping_error(s):
    assert parse(s) == None
    assert lox.had_error
    

@pytest.mark.parametrize('s', [
    '?:',
    '42 ? : 3',
    '42 ? 3 :',
    '? 42 : 3',
    '42 ?',
    '42 ? 3 ? 3 : 3',
    '42 ? 3'
])
def test_conditional_error(s):
    assert parse(s) == None
    assert lox.had_error

def test_aunt_sally():
    e = parse('1 != 2 - 1 * -3')
    assert e.operator.type == TT.BANG_EQUAL
    assert e.right.operator.type == TT.MINUS
    assert e.right.right.operator.type == TT.STAR
    assert isinstance(e.right.right.right, expr.Unary)
    assert e.right.right.right.operator.type == TT.MINUS
