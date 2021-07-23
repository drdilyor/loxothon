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
    BREAK               = 51
    CLASS               = 52
    ELSE                = 53
    FALSE               = 54
    FUN                 = 55
    FOR                 = 56
    IF                  = 57
    NIL                 = 58
    OR                  = 59
    PRINT               = 60
    RETURN              = 61
    SUPER               = 62
    THIS                = 63
    TRUE                = 64
    VAR                 = 65
    WHILE               = 66

    EOF                 = 0


# HACK: setting eq to True breaks this program:
#     for ( var i = 0; i < 10; i = i + 1 ) {
#       print i;
#     }
# BUT the *exact* program with different whitespace WORKS:
#     for (
#       var i = 0;
#       i < 10;
#       i = i + 1
#     ) {
#       print i;
#     }
# WTF IS GOING ON HERE? Cue mind exploding...

# OK, I dug a lot and found out... It is because Expr and Stmt are set eq=True
# and hashing *different* variable expr with *different* token but with those
# tokens having the same line number - returns the same number, the dict gets
# confused and our lox program blows up.

@dataclass(eq=False, frozen=True)
class Token:
    type: TokenType
    lexeme: str
    literal: Optional[str]
    line: int
    # def __init__(self, type, lexeme, literal, line):
    #     self.type = type
    #     self.lexeme = lexeme
    #     self.literal = literal

    def __str__(self): # pragma: no cover
        return f'{self.type} {self.lexeme} {self.literal}'

    # def __hash__(self):
    #     return hash(self.type) ^ hash(self.lexeme) ^ hash(self.literal)
    #
    # def __eq__(self, other):
    #     return self is other
    #     return self.type == other.type and self.lexeme == other.lexeme and self.literal == other.literal

    # @property
    # def line(self):
    #     return 0


__all__ = [
    'TokenType',
    'Token',
]
