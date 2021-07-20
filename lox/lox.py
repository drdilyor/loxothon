import sys

from lox.scanner import Scanner


had_error = False

def run_file(path: str) -> None:
    with open(path) as f:
        code = f.read()
    run(code)
    if had_error:
        sys.exit(65)


def run_prompt() -> None:
    global had_error
    while True:
        print(end='> ')
        try:
            run(input())
        except KeyboardInterrupt:
            break
        had_error = False


def run(source) -> None:
    scanner = Scanner(source)
    tokens = scanner.scan_tokens()

    for token in tokens:
        print(token)


def error(line: int, message: str) -> None:
    report(line, '', message)


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
