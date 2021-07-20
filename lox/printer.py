import lox.expr as expr

class AstPrinter(expr.Visitor[str]):
    def print(self, e: expr.Expr):
        return e.accept(self)

    def parens(self, name: str, *exprs: expr.Expr) -> str:
        return f'({name} {" ".join(i.accept(self) for i in exprs)})'

    def visitBinaryExpr(self, e: expr.Binary) -> str:
        return self.parens(e.operator.lexeme, e.left, e.right)

    def visitConditionalExpr(self, e: expr.Conditional) -> str:
        return self.parens('?:',  e.condition, e.then_branch, e.else_branch)

    def visitGroupingExpr(self, e: expr.Grouping) -> str:
        return self.parens('group', e.expression)

    def visitLiteralExpr(self, e: expr.Literal) -> str:
        return 'nil' if e.value is None else str(e.value)
    
    def visitUnaryExpr(self, e: expr.Unary) -> str:
        return self.parens(e.operator.lexeme, e.right)


__all__ = ['AstPrinter']

if __name__ == '__main__':
    from lox.token import Token, TokenType
    print(AstPrinter().print(
        expr.Binary(
            expr.Unary(
                Token(TokenType.MINUS, '-', None, 1),
                expr.Literal(123)),
            Token(TokenType.STAR, '*', None, 1),
            expr.Grouping(
                expr.Conditional(
                    expr.Literal(True),
                    expr.Literal(42),
                    expr.Literal(0))))))
