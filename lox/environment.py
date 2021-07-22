from typing import Any

from lox.error import LoxRuntimeError
from lox.token import Token


class Environment:
    def __init__(self):
        self.values: dict[str, object] = {}

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
            raise LoxRuntimeError(name, f"Undefined variable '{name.lexeme}'.")


__all__ = ['Environment']
