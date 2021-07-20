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
            return

        elif c in self.double_char:
            m = self.double_char[c]
            if not self.is_at_end and self.peek() in m:
                self.add_token(m[self.advance()])
            else:
                self.add_token(m[''])
            return

        lox.error(self.line, 'Unexpected character.')

    @property
    def is_at_end(self):
        return self.current >= len(self.source)

    def advance(self) -> str:
        c = self.source[self.current]
        self.current += 1
        return c

    def peek(self) -> str:
        print(self.current)
        return self.source[self.current]

    def add_token(self, type: TokenType, literal: Any = None):
        text = self.source[self.start:self.current]
        self.tokens.append(Token(type, text, literal, self.line))
