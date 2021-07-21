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
