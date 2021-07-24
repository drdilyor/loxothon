from typing import Union, List, Type, Tuple

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

    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.current = 0
        # Took a look into answers - I couldn't implement it myself 😅
        self.allow_expressions = False
        self.found_expression = False

    def parse(self) -> List[stmt.Stmt]:
        """Parses tokens and returns Statement list"""
        statements = []
        while not self.is_at_end:
            statements.append(self.declaration())

        return statements

    def parse_repl(self) -> Union[List[stmt.Stmt], expr.Expr]:
        self.allow_expressions = True
        statements = []
        while not self.is_at_end:
            statements.append(self.declaration())

            if self.found_expression:
                e: stmt.Expression = statements[-1]  # noqa
                return e.expression
            self.allow_expressions = False

        return statements

    def declaration(self) -> stmt.Stmt:
        try:
            if self.match(TT.FUN):
                return self.fun_declaration(kind='function')
            if self.match(TT.VAR):
                return self.var_declaration()
            return self.statement()
        except ParseError:
            self.synchronize()

    def fun_declaration(self, kind: str) -> stmt.Stmt:
        name = self.consume(TT.IDENTIFIER, f'Expect {kind} name.')
        self.consume(TT.LEFT_PAREN, f"Expect '(' {kind} name.")
        parameters = []

        if not self.is_at_end and self.peek().type != TT.RIGHT_PAREN:
            first = True
            while first or self.match(TT.COMMA):
                first = False

                if len(parameters) >= 255:
                    self.error(self.peek(),
                               "Can't have more than 255 parameters.")
                parameters.append(self.consume(TT.IDENTIFIER,
                                               'Expect parameter name'))
        self.consume(TT.RIGHT_PAREN, "Expect ')' after parameters")

        self.consume(TT.LEFT_BRACE, f"Expect '{{' before {kind} body.")
        body = self.block()
        return stmt.Function(name, parameters, body)

    def var_declaration(self) -> stmt.Stmt:
        name = self.consume(TT.IDENTIFIER, 'Expect variable name.')
        initializer = self.expression() if self.match(TT.EQUAL) else None
        self.consume(TT.SEMICOLON, "Expect ';' after variable declaration.")
        return stmt.Var(name, initializer)

    def statement(self) -> stmt.Stmt:
        if self.match(TT.BREAK):
            return self.break_statement()
        if self.match(TT.FOR):
            return self.for_statement()
        if self.match(TT.IF):
            return self.if_statement()
        if self.match(TT.PRINT):
            return self.print_statement()
        if self.match(TT.RETURN):
            return self.return_statement()
        if self.match(TT.WHILE):
            return self.while_statement()
        if self.match(TT.LEFT_BRACE):
            return stmt.Block(self.block())
        return self.expression_statement()

    def break_statement(self) -> stmt.Stmt:
        keyword = self.previous()
        self.consume(TT.SEMICOLON, "Expect ';' after 'break'.")
        return stmt.Break(keyword)

    def for_statement(self) -> stmt.Stmt:
        self.consume(TT.LEFT_PAREN, "Expect '(' after 'for'.")

        if self.match(TT.SEMICOLON):
            initializer = None
        elif self.match(TT.VAR):
            initializer = self.var_declaration()
        else:
            initializer = self.expression_statement()

        condition = None
        if not self.is_at_end and self.peek().type != TT.SEMICOLON:
            condition = self.expression()
        self.consume(TT.SEMICOLON, "Expect ';' after loop condition.")

        increment = None
        if not self.is_at_end and self.peek().type != TT.RIGHT_PAREN:
            increment = self.expression()
        self.consume(TT.RIGHT_PAREN, "Expect ')' after for clauses.")

        body = self.statement()

        if increment:
            body = stmt.Block([body, stmt.Expression(increment)])

        body = stmt.While(condition or expr.Literal(True), body)

        if initializer:
            body = stmt.Block([initializer, body])

        return body

    def if_statement(self) -> stmt.If:
        self.consume(TT.LEFT_PAREN, "Expect '(' after 'if'.")
        condition = self.expression()
        self.consume(TT.RIGHT_PAREN, "Expect ')' after 'if'")
        then_branch = self.statement()
        else_branch = self.statement() if self.match(TT.ELSE) else None
        return stmt.If(condition, then_branch, else_branch)

    def print_statement(self) -> stmt.Stmt:
        e = self.expression()
        self.consume(TT.SEMICOLON, "Expect ';' after value.")
        return stmt.Print(e)

    def return_statement(self) -> stmt.Stmt:
        keyword = self.previous()
        value = None
        if not self.is_at_end and self.peek().type != TT.SEMICOLON:
            value = self.expression()
        self.consume(TT.SEMICOLON, "Expect ';' after return value.")
        return stmt.Return(keyword, value)

    def while_statement(self) -> stmt.Stmt:
        self.consume(TT.LEFT_PAREN, "Expect '(' after 'while'.")
        condition = self.expression()
        self.consume(TT.RIGHT_PAREN, "Expect ')' after condition.")
        body = self.statement()
        return stmt.While(condition, body)

    def expression_statement(self) -> stmt.Stmt:
        e = self.expression()
        if self.allow_expressions and self.is_at_end:
            self.found_expression = True
        else:
            self.consume(TT.SEMICOLON, "Expect ';' after expression.")
        return stmt.Expression(e)

    def block(self):
        statements = []
        while not self.is_at_end and self.peek().type != TT.RIGHT_BRACE:
            statements.append(self.declaration())

        self.consume(TT.RIGHT_BRACE, "Expect '}' after block.")
        return statements

    def binary_left(
        self, upnext, types: Tuple[TT, ...],
        expr_class: Type[Union[expr.Binary, expr.Logical]] = expr.Binary
    ) -> expr.Expr:
        # A helper for parsing left-associative binary expression
        e = upnext()

        while self.match(*types):
            operator = self.previous()
            right = upnext()
            e = expr_class(e, operator, right)  # noqa

        return e

    def expression(self):
        return self.comma()

    def comma(self):
        return self.binary_left(self.assignment, (TT.COMMA,))

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
        e = self.logic_or()

        if self.match(TT.QUESTION):
            then_branch = self.expression()
            self.consume(
                TT.COLON,
                "Expect ':' after then branch of conditional expression")
            else_branch = self.conditional()
            e = expr.Conditional(e, then_branch, else_branch)

        return e

    def logic_or(self) -> expr.Expr:
        return self.binary_left(self.logic_and, (TT.OR,), expr.Logical)

    def logic_and(self) -> expr.Expr:
        return self.binary_left(self.equality, (TT.AND,), expr.Logical)

    def equality(self):
        return self.binary_left(self.comparison,
                                (TT.BANG_EQUAL, TT.EQUAL_EQUAL))

    def comparison(self):
        return self.binary_left(
            self.term, (TT.GREATER, TT.GREATER_EQUAL, TT.LESS, TT.LESS_EQUAL))

    def term(self):
        return self.binary_left(self.factor, (TT.MINUS, TT.PLUS))

    def factor(self):
        return self.binary_left(self.unary, (TT.SLASH, TT.STAR))

    def unary(self) -> expr.Expr:
        if self.match(TT.BANG, TT.MINUS):
            operator = self.previous()
            right = self.unary()
            return expr.Unary(operator, right)

        return self.call()

    def call(self) -> expr.Expr:
        e = self.primary()
        while True:
            if self.match(TT.LEFT_PAREN):
                e = self.finish_call(e)
            # not sure why this is here
            else:
                break  # pragma: no cover
        return e

    def finish_call(self, callee: expr.Expr):
        arguments = []
        if not self.is_at_end and self.peek().type != TT.RIGHT_PAREN:
            while not arguments or self.match(TT.COMMA):
                if len(arguments) >= 255:
                    self.error(self.peek(),
                               "Can't have more than 255 arguments")
                arguments.append(self.assignment())

        paren = self.consume(TT.RIGHT_PAREN, "Expect ')' after arguments.")
        return expr.Call(callee, paren, arguments)

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
