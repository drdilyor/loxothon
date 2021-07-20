from typing import Any

from lox.token import Token, TokenType
from lox import lox


class Scanner:
    single_char = {
        '(': TokenType.LEFT_PAREN,
        ')': TokenType.RIGHT_PAREN,
        '{': TokenType.LEFT_BRACE,
        '}': TokenType.RIGHT_BRACE,
        ',': TokenType.COMMA,
        '.': TokenType.DOT,
        '-': TokenType.MINUS,
        '+': TokenType.PLUS,
        ';': TokenType.SEMICOLON,
        '*': TokenType.STAR,
    }
    double_char = {
        '!': {
            '': TokenType.BANG,
            '=': TokenType.BANG_EQUAL,
        },
        '=': {
            '': TokenType.EQUAL,
            '=': TokenType.EQUAL_EQUAL,
        },
        '>': {
            '': TokenType.GREATER,
            '=': TokenType.GREATER_EQUAL,
        },
        '<': {
            '': TokenType.LESS,
            '=': TokenType.LESS_EQUAL,
        },
    }
    whitespace = {' ', '\r', '\t'}

    def __init__(self, source: str):
        self.source = source
        self.tokens = []
        self.start = 0
        self.current = 0
        self.line = 1

    def scan_tokens(self) -> list[Token]:
        while not self.is_at_end:
            self.start = self.current
            self.scan_token()
        self.tokens.append(Token(TokenType.EOF, '', None, self.line))
        return self.tokens

    def scan_token(self) -> None:
        c = self.advance()
        if c in self.single_char:
            self.add_token(self.single_char[c])

        elif c in self.double_char:
            m = self.double_char[c]
            if self.peek() in m:
                self.add_token(m[self.advance()])
            else:
                self.add_token(m[''])

        elif c == '/':
            if self.match('/'):
                while self.peek() != '\n' and not self.is_at_end:
                    self.advance()
            else:
                self.add_token(TokenType.SLASH)

        elif c in self.whitespace:
            pass

        elif c == '\n':
            self.line += 1

        elif c == '"':
            self.string()

        elif self.is_digit(c):
            self.number()

        else:
            lox.error(self.line, 'Unexpected character.')

    def string(self):
        while self.peek() != '"' and not self.is_at_end:
            if self.peek() == '\n':
                line += 1
            self.advance()

        if self.is_at_end:
            lox.error(line, 'Unterminated string.')
            return

        self.advance()

        value = self.source[self.start + 1 : self.current - 1]
        self.add_token(TokenType.STRING, value)

    def number(self):
        while self.is_digit(self.peek()):
            self.advance()

        # Look for a fraction part
        if self.peek() == '.' and self.is_digit(self.peek_next()):
            # consume the '.'
            self.advance()

            while self.is_digit(self.peek()):
                self.advance()

        self.add_token(TokenType.NUMBER, float(self.source[self.start:self.current]))


    @property
    def is_at_end(self):
        return self.current >= len(self.source)

    def advance(self) -> str:
        c = self.source[self.current]
        self.current += 1
        return c

    def peek(self) -> str:
        if self.is_at_end:
            return '\0'
        return self.source[self.current]

    def peek_next(self) -> str:
        if self.current + 1 >= len(self.source):
            return '\0'
        return self.source[self.current + 1]

    def match(self, c: str) -> bool:
        if self.is_at_end or self.source[self.current] != c:
            return False
        self.current += 1
        return True

    def is_digit(self, c: str):
        return ord('0') <= ord(c) <= ord('9')

    def add_token(self, type: TokenType, literal: Any = None):
        text = self.source[self.start:self.current]
        self.tokens.append(Token(type, text, literal, self.line))
