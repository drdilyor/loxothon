from typing import Any, Optional

from lox.error import LoxRuntimeError
from lox.token import Token


class Environment:
    def __init__(self, enclosing: Optional['Environment'] = None):
        self.values: dict[str, object] = {}
        self.enclosing = enclosing

    def define(self, name: str, value: object) -> None:
        self.values[name] = value

    def assign(self, name: Token, value: object):
        if name.lexeme in self.values:
            self.values[name.lexeme] = value
        else:
            raise LoxRuntimeError(name, f"Undefined variable '{name.lexeme}'.")

    def get(self, name: Token) -> object:
        try:
            return self.values[name.lexeme]
        except KeyError:
            if self.enclosing:
                return self.enclosing.get(name)
            raise LoxRuntimeError(name, f"Undefined variable '{name.lexeme}'.")


__all__ = ['Environment']
