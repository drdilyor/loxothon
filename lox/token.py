import enum
from typing import Optional, NamedTuple


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
    SET                 = 57
    IF                  = 58
    NIL                 = 59
    OR                  = 60
    PRINT               = 61
    RETURN              = 62
    SUPER               = 63
    THIS                = 64
    TRUE                = 65
    VAR                 = 66
    WHILE               = 67

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

class Token(NamedTuple):
    type: TokenType
    lexeme: str
    literal: Optional[str]
    line: int

    def __str__(self):  # pragma: no cover
        return f'{self.type} {self.lexeme} {self.literal}'


__all__ = [
    'TokenType',
    'Token',
]
