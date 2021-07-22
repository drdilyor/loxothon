import lox.expr as expr
import lox.stmt as stmt

# untested


class AstPrinter(expr.Visitor[str], stmt.Visitor[str]):
    def print(self, s: list[stmt.Stmt]):
        return '\n'.join(i.accept(self) for i in s)

    def parens(self, name: str, *exprs: expr.Expr) -> str:
        return f'({name} {" ".join(i.accept(self) for i in exprs)})'

    def visit_block_stmt(self, s: stmt.Block) -> str:
        result = '\n'.join(i.accept(self) for i in s.statements)
        result = '\n'.join('  ' + i for i in result.split('\n'))
        return f'(block \n{result})'

    def visit_expression_stmt(self, s: stmt.Expression) -> str:
        return self.parens('expression', s.expression)

    def visit_if_stmt(self, s: stmt.If) -> str:
        return self.parens('if', s.condition, s.then_branch, s.else_branch)

    def visit_print_stmt(self, s: stmt.Print) -> str:
        return self.parens('print', s.expression)

    def visit_var_stmt(self, s: stmt.Var) -> str:
        return self.parens(f'var {s.name}', s.initializer)

    def visit_while_stmt(self, s: stmt.While) -> str:
        return self.parens('while', s.condition, s.body)

    def visit_assign_expr(self, e: expr.Assign) -> str:
        return self.parens(f'= {e.name}', e.value)

    def visit_binary_expr(self, e: expr.Binary) -> str:
        return self.parens(e.operator.lexeme, e.left, e.right)

    def visit_conditional_expr(self, e: expr.Conditional) -> str:
        return self.parens('?:',  e.condition, e.then_branch, e.else_branch)

    def visit_grouping_expr(self, e: expr.Grouping) -> str:
        return self.parens('group', e.expression)

    def visit_literal_expr(self, e: expr.Literal) -> str:
        return 'nil' if e.value is None else str(e.value)

    def visit_logical_expr(self, e: expr.Logical) -> str:
        return self.parens(e.operator.lexeme, e.left, e.right)

    def visit_unary_expr(self, e: expr.Unary) -> str:
        return self.parens(e.operator.lexeme, e.right)

    def visit_variable_expr(self, e: expr.Variable) -> str:
        return f'(variable {e.name.lexeme})'


__all__ = ['AstPrinter']
