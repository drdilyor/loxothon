import re
from pathlib import Path

import pytest

from lox import Parser, Interpreter, Scanner

def gather_tests():
    cdir = Path(__file__).parent.absolute()
    results = []

    for file in cdir.glob('**/*.lox'):
        with open(file) as f:
            source = f.read()
        expects = re.findall(r'print .*;\s*//\s*expect: (.*)', source)
        expect = ''.join(f'{i}\n' for i in expects)
        results.append((source, expect))

    return results


@pytest.mark.parametrize('s,expect', gather_tests())
def test_interpreter(s, expect, capsys):
    Interpreter().interpret(Parser(Scanner(s).scan_tokens()).parse())
    assert capsys.readouterr().out == expect

