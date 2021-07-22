import re
from pathlib import Path

import pytest

from lox import Parser, Interpreter, Scanner, lox

expect_error = object()
expect_runtime_error = object()


@pytest.fixture(autouse=True)
def reset_had_error():
    lox.had_error = False
    lox.had_runtime_error = False


def gather_tests():
    cdir = Path(__file__).parent.absolute()
    results = []

    for file in cdir.glob('**/*.lox'):
        with open(file) as f:
            source = f.read()
        if source.startswith('// expect: runtime-error'):
            results.append((source, expect_runtime_error))
        elif source.startswith('// expect: error'):
            results.append((source, expect_error))
        else:
            expects = re.findall(r'print .*;\s*//\s*expect: (.*)', source)
            expect = ''.join(f'{i}\n' for i in expects)
            results.append((source, expect))

    return results


@pytest.mark.parametrize('s,expect', gather_tests())
def test_interpreter(s, expect, capsys):
    statements = Parser(Scanner(s).scan_tokens()).parse()
    if lox.had_error:
        assert expect is expect_error
        return

    Interpreter().interpret(statements)
    if expect is expect_runtime_error:
        assert lox.had_runtime_error
    else:
        assert capsys.readouterr().out == expect


