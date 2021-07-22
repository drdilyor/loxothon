from lox import Parser, Scanner, lox


def parse(s):
    return Parser(Scanner(s).scan_tokens()).parse()


def test_panic_falls_to_declaration(capsys):
    s = parse("""
    var a = 42 while TODO foo;
    while blah yes no;
    """)
    assert s == [None, None]
    errors = capsys.readouterr().out
    # make sure it reports two parse errors (the whole point of synchronizing)
    assert len(errors.strip().split('\n')) == 2
    assert lox.had_error
