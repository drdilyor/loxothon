from pathlib import Path
import re
from typing import Tuple, List

import pytest

from lox import Parser, Interpreter, Scanner, lox, Resolver

expect_error = object()
expect_resolve_error = object()
expect_runtime_error = object()


@pytest.fixture(autouse=True)
def reset_had_error():
    lox.had_error = False
    lox.had_runtime_error = False

def removeprefix(p: str, s: str) -> str:
    return (s, s[len(p):])[s.startswith(p)]

def gather_tests() -> Tuple[List[Tuple[str, object]], List[str]]:
    cdir = Path(__file__).parent
    results = []
    ids = []

    for file in cdir.glob('**/*.lox'):
        with open(file) as f:
            source = f.read()
        ids.append(removeprefix('/', removeprefix(str(cdir), str(file))))

        if source.startswith('// expect: runtime-error'):
            results.append((source, expect_runtime_error))
        elif source.startswith('// expect: resolve-error'):
            results.append((source, expect_resolve_error))
        elif source.startswith('// expect: error'):
            results.append((source, expect_error))
        else:
            # I know, it is dumb.
            expects = re.findall(r'.*;\s*//\s*expect: (.*)', source)
            expect = ''.join(f'{i}\n' for i in expects)
            results.append((source, expect))

    return results, ids


tests = gather_tests()

@pytest.mark.parametrize('s,expect', tests[0], ids=tests[1])
def test_interpreter(s, expect, capsys):
    statements = Parser(Scanner(s).scan_tokens()).parse()
    if lox.had_error:
        assert expect is expect_error
        return

    interpreter = Interpreter()
    Resolver(interpreter).resolve(statements)
    if expect is expect_resolve_error:
        assert lox.had_error
        return

    assert not lox.had_error
    interpreter.interpret(statements)
    if expect is expect_runtime_error:
        assert lox.had_runtime_error
    else:
        assert capsys.readouterr().out == expect


