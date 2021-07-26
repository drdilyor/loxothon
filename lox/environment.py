from typing import Optional, Dict

import lox


class Environment:
    def __init__(self, enclosing: Optional['Environment'] = None):
        self.values: Dict[str, object] = {}
        self.enclosing = enclosing

    def define(self, name: str, value: object) -> None:
        self.values[name] = value

    def ancestor(self, distance: int) -> 'Environment':
        environment = self
        for i in range(distance):
            environment = environment.enclosing
        return environment

    def get(self, name: 'lox.Token') -> object:
        try:
            return self.values[name.lexeme]
        except KeyError:
            if self.enclosing:
                # this is not used anymore
                return self.enclosing.get(name)  # pragma: no cover
            raise lox.LoxRuntimeError(
                name, f"Undefined variable '{name.lexeme}'.")

    def get_at(self, distance: int, name: str) -> object:
        return self.ancestor(distance).values.get(name)

    def assign(self, name: 'lox.Token', value: object):
        if name.lexeme in self.values:
            self.values[name.lexeme] = value
        else:
            if self.enclosing:
                # this is not used anymore
                return self.enclosing.assign(name, value)  # pragma: no cover
            raise lox.LoxRuntimeError(
                name, f"Undefined variable '{name.lexeme}'.")

    def assign_at(self, distance: int, name: 'lox.Token', value: object):
        self.ancestor(distance).values[name.lexeme] = value


__all__ = ['Environment']
