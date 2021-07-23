from typing import Optional

from lox.error import LoxRuntimeError
from lox.token import Token


class Environment:
    def __init__(self, enclosing: Optional['Environment'] = None):
        self.values: dict[str, object] = {}
        self.enclosing = enclosing

    def define(self, name: str, value: object) -> None:
        self.values[name] = value

    def ancestor(self, distance: int) -> 'Environment':
        environment = self
        for i in range(distance):
            environment = environment.enclosing
        return environment

    def get(self, name: Token) -> object:
        try:
            return self.values[name.lexeme]
        except KeyError:
            if self.enclosing:
                return self.enclosing.get(name)
            raise LoxRuntimeError(name, f"Undefined variable '{name.lexeme}'.")

    def get_at(self, distance: int, name: str) -> object:
        return self.ancestor(distance).values.get(name)

    def assign(self, name: Token, value: object):
        if name.lexeme in self.values:
            self.values[name.lexeme] = value
        else:
            if self.enclosing:
                return self.enclosing.assign(name, value)
            raise LoxRuntimeError(name, f"Undefined variable '{name.lexeme}'.")

    def assign_at(self, distance: int, name: Token, value: object):
        self.ancestor(distance).values[name.lexeme] = value


__all__ = ['Environment']
