import re
from pathlib import Path

import pytest

from lox import Parser, Interpreter, Scanner, lox

expect_error = object()
expect_runtime_error = object()


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
    Interpreter().interpret(Parser(Scanner(s).scan_tokens()).parse())
    if expect is expect_runtime_error:
        assert lox.had_runtime_error
    elif expect is expect_error:
        assert lox.had_error
    else:
        assert capsys.readouterr().out == expect


