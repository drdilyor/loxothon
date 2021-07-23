#!/usr/bin/env python3
import sys

import lox

def main(file = None, *rest):
    if rest:
        print('Usage: python lox.py [script]')
        sys.exit(64)
    elif file:
        lox.run_file(file)
    else:
        lox.run_prompt()


if __name__ == '__main__':
    main(*sys.argv[1:])
