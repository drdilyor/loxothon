import sys

from lox.interpreter import Interpreter
from lox.error import LoxRuntimeError
from lox.scanner import Scanner
from lox.parser import Parser
from lox.printer import AstPrinter
from lox.token import Token, TokenType


had_error = False
had_runtime_error = False


def run_file(path: str) -> None:
    with open(path) as f:
        code = f.read()
    run(code, Interpreter())
    if had_error:
        sys.exit(65)
    if had_runtime_error:
        sys.exit(70)


def run_prompt() -> None:
    import lox.stmt as stmt

    global had_error
    interpreter = Interpreter()
    debug = False
    while True:
        print(end='> ')
        try:
            source = input()
            if source == '.debug on':
                debug = True
                print('turned debug on')
            else:

                tokens = Scanner(source).scan_tokens()
                if debug:
                    for token in tokens:
                        print(token)

                statements = Parser(tokens).parse_repl()
                if debug:
                    print(AstPrinter().print(statements))

                if had_error:
                    continue

                if isinstance(statements, list):
                    interpreter.interpret(statements)
                else:
                    value = interpreter.interpret_expression(statements)
                    print(f'= {interpreter.stringify(value)}')

        except KeyboardInterrupt:
            break
        had_error = False


def run(source: str, interpreter: Interpreter) -> None:
    global had_error
    scanner = Scanner(source)
    tokens = scanner.scan_tokens()

    statements = Parser(tokens).parse()
    if had_error:
        return

    interpreter.interpret(statements)


def error(line: int, message: str) -> None:
    report(line, '', message)


def error_token(token: Token, message: str) -> None:
    if token.type == TokenType.EOF:
        report(token.line, ' at end', message)
    else:
        report(token.line, f" at '{token.lexeme}'", message)


def runtime_error(e: LoxRuntimeError):
    global had_runtime_error
    print(f'[line {e.token.line}] {e.message}')
    had_runtime_error = True


def report(line: int, where: str, message: str) -> None:
    global had_error
    print(f'[line {line}] Error{where}: {message}')
    had_error = True


__all__ = [
    'run_prompt',
    'run_file',
    'run',
    'error',
]
