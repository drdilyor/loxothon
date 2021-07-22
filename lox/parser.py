import lox.expr as expr
import lox.lox as lox
import lox.stmt as stmt
from lox.token import Token, TokenType as TT


class ParseError(ValueError):
    pass


class Parser:
    syncpoints = {
        TT.CLASS,
        TT.VAR,
        TT.FOR,
        TT.IF,
        TT.WHILE,
        TT.PRINT,
        TT.RETURN,
    }

    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.current = 0

    def parse(self) -> list[stmt.Stmt]:
        """Parses tokens and returns Statement list"""
        statements = []
        while not self.is_at_end:
            statements.append(self.declaration())

        return statements

    def declaration(self) -> stmt.Stmt:
        try:
            if self.match(TT.VAR):
                return self.var_declaration()
            return self.statement()
        except ParseError:
            self.synchronize()

    def var_declaration(self) -> stmt.Stmt:
        name = self.consume(TT.IDENTIFIER, 'Expect variable name.')
        initializer = self.expression() if self.match(TT.EQUAL) else None
        self.consume(TT.SEMICOLON, "Expect ';' after variable declaration.")
        return stmt.Var(name, initializer)

    def statement(self) -> stmt.Stmt:
        if self.match(TT.PRINT):
            return self.print_statement()
        return self.expression_statement()

    def print_statement(self) -> stmt.Stmt:
        e = self.expression()
        self.consume(TT.SEMICOLON, "Expect ';' after value.")
        return stmt.Print(e)

    def expression_statement(self) -> stmt.Stmt:
        e = self.expression()
        self.consume(TT.SEMICOLON, "Expect ';' after expression.")
        return stmt.Expression(e)

    def binary_left(self, upnext, *types: TT) -> expr.Expr:
        # A helper for parsing left-associative binary expression
        e = upnext()

        while self.match(*types):
            operator = self.previous()
            right = upnext()
            e = expr.Binary(e, operator, right)

        return e

    def expression(self):
        return self.comma()

    def comma(self):
        return self.binary_left(self.assignment, TT.COMMA)

    def assignment(self) -> expr.Expr:
        e = self.conditional()

        if self.match(TT.EQUAL):
            equals = self.previous()
            value = self.assignment()

            if isinstance(e, expr.Variable):
                return expr.Assign(e.name, value)

            self.error(equals, 'Invalid assignment target.')

        return e

    def conditional(self) -> expr.Expr:
        e = self.equality()

        if self.match(TT.QUESTION):
            then_branch = self.expression()
            self.consume(
                TT.COLON,
                "Expect ':' after then branch of conditional expression")
            else_branch = self.conditional()
            e = expr.Conditional(e, then_branch, else_branch)

        return e

    def equality(self):
        return self.binary_left(self.comparison, TT.BANG_EQUAL, TT.EQUAL_EQUAL)

    def comparison(self):
        return self.binary_left(
            self.term, TT.GREATER, TT.GREATER_EQUAL, TT.LESS, TT.LESS_EQUAL)

    def term(self):
        return self.binary_left(self.factor, TT.MINUS, TT.PLUS)

    def factor(self):
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

        if self.match(TT.IDENTIFIER):
            return expr.Variable(self.previous())

        if self.match(TT.LEFT_PAREN):
            e = self.expression()
            self.consume(TT.RIGHT_PAREN, "Expect ')' after expression.")
            return expr.Grouping(e)

        raise self.error(self.peek(), 'Unexpected expression.')

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
            return False

        if self.peek().type in types:
            self.advance()
            return True
        return False

    def consume(self, type: TT, message: str) -> Token:
        if self.peek().type == type:
            return self.advance()
        raise self.error(self.peek(), message)

    def error(self, token: Token, message: str) -> ParseError:
        lox.error_token(token, message)
        return ParseError()

    def synchronize(self) -> None:  # pragma: no cover
        self.advance()
        while not self.is_at_end:
            if (self.previous().type == TT.SEMICOLON
               or self.peek().type in self.syncpoints):
                return
            self.advance()


__all__ = ['Parser', 'ParseError']
