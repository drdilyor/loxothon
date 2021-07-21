import lox.expr as expr
import lox.stmt as stmt


class AstPrinter(expr.Visitor[str], stmt.Visitor[str]):
    def print(self, s: list[stmt.Stmt]):
        return '\n'.join(i.accept(self) for i in s)

    def parens(self, name: str, *exprs: expr.Expr) -> str:
        return f'({name} {" ".join(i.accept(self) for i in exprs)})'

    def visit_expression_stmt(self, s: stmt.Expression) -> str:
        return self.parens('expression', s.expression)

    def visit_print_stmt(self, s: stmt.Print) -> str:
        return self.parens('print', s.expression)

    # again, vim saved me hours "recasing" these methods
    def visit_binary_expr(self, e: expr.Binary) -> str:
        return self.parens(e.operator.lexeme, e.left, e.right)

    def visit_conditional_expr(self, e: expr.Conditional) -> str:
        return self.parens('?:',  e.condition, e.then_branch, e.else_branch)

    def visit_grouping_expr(self, e: expr.Grouping) -> str:
        return self.parens('group', e.expression)

    def visit_literal_expr(self, e: expr.Literal) -> str:
        return 'nil' if e.value is None else str(e.value)

    def visit_unary_expr(self, e: expr.Unary) -> str:
        return self.parens(e.operator.lexeme, e.right)


__all__ = ['AstPrinter']
