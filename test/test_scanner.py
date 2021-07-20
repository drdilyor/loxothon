import pytest

from lox import Scanner, TokenType
import lox.lox as lox

@pytest.fixture(autouse=True)
def set_had_error_false():
    try:
        yield
    finally:
        lox.had_error = False

def test_has_eof():
    tokens = Scanner('').scan_tokens()
    assert tokens[-1].type == TokenType.EOF

def test_discards_whitespace():
    tokens = Scanner(' \t\n\f\v').scan_tokens()
    assert len(tokens) == 1

def test_unknown_char():
    tokens = Scanner('#\a\0').scan_tokens()
    assert len(tokens) - 1 == 0
    assert lox.had_error

def test_single_char():
    source = '(){};+-*.,'
    tokens = Scanner(source).scan_tokens()
    assert len(tokens) - 1 == len(source)

def test_double_single_char():
    tokens = Scanner('= ! < >').scan_tokens()
    assert len(tokens) - 1 == 4

def test_double_char():
    tokens = Scanner('<= >= != ==').scan_tokens()
    assert len(tokens) - 1 == 4

def test_slash():
    tokens = Scanner('/').scan_tokens()
    assert len(tokens) - 1 == 1
    assert tokens[0].type == TokenType.SLASH
    tokens = Scanner('/ + -').scan_tokens()
    assert len(tokens) - 1 == 3
    assert tokens[0].type == TokenType.SLASH

def test_comment():
    tokens = Scanner('// this is comment foo bar foo bar').scan_tokens()
    assert len(tokens) - 1 == 0
    tokens = Scanner('{} // comment').scan_tokens()
    types = [i.type for i in tokens]
    assert len(tokens) - 1 == 2
    assert types == [TokenType.LEFT_BRACE, TokenType.RIGHT_BRACE, TokenType.EOF]

def test_comment_until_newline():
    tokens = Scanner('// comment\n+').scan_tokens()
    assert len(tokens) - 1 == 1

def test_block_comment():
    tokens = Scanner('/* comment */').scan_tokens()
    assert len(tokens) - 1 == 0

def test_block_comment_nest():
    tokens = Scanner('/* comment /* inside */ comment */').scan_tokens()
    assert len(tokens) - 1 == 0

def test_block_comment_unterminated():
    tokens = Scanner('/* comment').scan_tokens()
    assert lox.had_error == True

    tokens = Scanner('/* comment /* */').scan_tokens()
    assert lox.had_error == True

@pytest.mark.parametrize('source', ['//* comment', '// /* comment'])
def test_block_comment_after_comment(source):
    tokens = Scanner(source).scan_tokens()
    assert len(tokens) - 1 == 0
    assert lox.had_error == False

@pytest.mark.parametrize('identifier', ['myvar', '_', 'Capital_Letters', 'number99'])
def test_identifier(identifier):
    tokens = Scanner(identifier).scan_tokens()
    assert len(tokens) - 1 == 1
    assert tokens[0].type == TokenType.IDENTIFIER

@pytest.mark.parametrize('source,literal', [('0', 0.0), ('999', 999.0), ('1.5', 1.5)])
def test_number(source, literal):
    tokens = Scanner(source).scan_tokens()
    assert len(tokens) - 1 == 1
    assert tokens[0].type == TokenType.NUMBER
    assert tokens[0].literal == literal

def test_number_dot_identifier():
    tokens = Scanner('42.question').scan_tokens()
    types = [i.type for i in tokens]
    assert len(tokens) - 1 == 3
    assert types == [TokenType.NUMBER, TokenType.DOT,
                     TokenType.IDENTIFIER, TokenType.EOF]
    assert tokens[0].literal == 42.0

def test_number_dot_eof():
    tokens = Scanner('42.').scan_tokens()
    types = [i.type for i in tokens]
    assert len(tokens) - 1 == 2
    assert types == [TokenType.NUMBER, TokenType.DOT, TokenType.EOF]
    assert tokens[0].literal == 42.0

def test_string():
    tokens = Scanner('"string"').scan_tokens()
    assert len(tokens) - 1 == 1
    assert tokens[0].type == TokenType.STRING
    assert tokens[0].literal == 'string'

def test_string_multiline():
    tokens = Scanner('"string\nmultiline"').scan_tokens()
    assert len(tokens) - 1 == 1
    assert tokens[0].literal == 'string\nmultiline'

def test_string_unterminated():
    tokens = Scanner('"oops').scan_tokens()
    assert len(tokens) - 1 == 0
    assert lox.had_error == True

def test_keywords():
    for keyword, type in Scanner.keywords.items():
        tokens = Scanner(keyword).scan_tokens()
        assert len(tokens) - 1 == 1
        assert tokens[0].type == type
