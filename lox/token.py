from typing import Optional

from dataclasses import dataclass
import enum


class TokenType(enum.Enum):
    LEFT_PAREN          = 1
    RIGHT_PAREN         = 2
    LEFT_BRACE          = 3
    RIGHT_BRACE         = 4
    COMMA               = 5
    DOT                 = 6
    MINUS               = 7
    PLUS                = 8
    SEMICOLON           = 9
    SLASH               = 10
    STAR                = 11
    QUESTION            = 12
    COLON               = 13

    BANG                = 30
    BANG_EQUAL          = 31
    EQUAL               = 32
    EQUAL_EQUAL         = 33
    GREATER             = 34
    GREATER_EQUAL       = 35
    LESS                = 36
    LESS_EQUAL          = 37

    IDENTIFIER          = 40
    STRING              = 41
    NUMBER              = 42

    AND                 = 50
    CLASS               = 50
    ELSE                = 51
    FALSE               = 52
    FUN                 = 53
    FOR                 = 54
    IF                  = 55
    NIL                 = 56
    OR                  = 57
    PRINT               = 58
    RETURN              = 59
    SUPER               = 60
    THIS                = 61
    TRUE                = 62
    VAR                 = 63
    WHILE               = 64

    EOF                 = 0


@dataclass
class Token:
    type: TokenType
    lexeme: str
    literal: Optional[str]
    line: int

    def __str__(self): # pragma: no cover
        return f'{self.type} {self.lexeme} {self.literal}'


__all__ = [
    'TokenType',
    'Token',
]
