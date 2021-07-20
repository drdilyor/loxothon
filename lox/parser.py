from typing import Optional

from lox.token import Token, TokenType as TT
import lox.expr as expr


class ParseError(ValueError):
    pass


class Parser:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.current = 0

    def parse(self) -> Optional[expr.Expr]:
        try:
            return self.expression()
        except ParseError as e:
            return None

    def binary_left(self, upnext, *types: TT) -> expr.Expr:
        # A helper for parsing left-associative binary expression
        e = upnext()

        while self.match(*types):
            operator = self.previous()
            right = upnext()
            e = expr.Binary(e, operator, right)

        return e

    def expression(self) -> expr.Expr:
        return self.equality()

    def equality(self) -> expr.Expr:
        return self.binary_left(self.comparison, TT.BANG_EQUAL, TT.EQUAL_EQUAL)

    def comparison(self) -> expr.Expr:
        return self.binary_left(
            self.term, TT.GREATER, TT.GREATER_EQUAL, TT.LESS, TT.LESS_EQUAL)

    def term(self) -> expr.Expr:
        return self.binary_left(self.factor, TT.MINUS, TT.PLUS)

    def factor(self) -> expr.Expr:
        return self.binary_left(self.unary, TT.SLASH, TT.STAR)

    def unary(self) -> expr.Expr:
        if self.match(TT.BANG, TT.MINUS):
            operator = self.previous()
            right = self.unary()
            return expr.Unary(operator, right)

        return self.primary()

    def primary(self) -> expr.Expr:
        if self.match(TT.FALSE):
            return expr.Literal(False)
        if self.match(TT.TRUE):
            return expr.Literal(True)
        if self.match(TT.NIL):
            return expr.Literal(None)

        if self.match(TT.NUMBER, TT.STRING):
            return expr.Literal(self.previous().literal)

        if self.match(TT.LEFT_PAREN):
            e = self.expression()
            self.consume(TT.RIGHT_PAREN, "Expect ')' after expression.")
            return expr.Grouping(e)

    @property
    def is_at_end(self) -> bool:
        return self.peek().type == TT.EOF

    def advance(self) -> Token:
        if not self.is_at_end:
            self.current += 1
        return self.previous()

    def peek(self) -> Token:
        return self.tokens[self.current]

    def previous(self) -> Token:
        return self.tokens[self.current - 1]

    def match(self, *types: TT) -> bool:
        if self.is_at_end:
            return

        if self.peek().type in types:
            self.advance()
            return True
        return False

    def consume(self, type: TT, message: str) -> None:
        if self.peek().type != type:
            raise ParseError(message)


__all__ = ['Parser']