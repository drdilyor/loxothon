from abc import ABC, abstractmethod
import time

import lox.stmt as stmt
from lox.environment import Environment
from lox.error import LoxReturn


class LoxCallable(ABC):
    @abstractmethod
    def call(self, interpreter, # *the* type: Interpreter
             arguments: list) -> object: ...

    @abstractmethod
    def arity(self) -> int: ...


class LoxClock(LoxCallable):
    def call(self, interpreter, arguments: list) -> object:
        return time.time()

    def arity(self) -> int:
        return 0

    def __str__(self):
        return '<native fun>'


lox_clock = LoxClock()


class LoxFunction(LoxCallable):
    def __init__(self, declaration: stmt.Function, closure: Environment):
        self.declaration = declaration
        self.closure = closure

    def call(self, interpreter, arguments: list) -> object:
        environment = Environment(self.closure)
        for param, argument in zip(self.declaration.params, arguments):
            environment.define(param.lexeme, argument)

        try:
            interpreter.execute_block(self.declaration.body, environment)
        except LoxReturn as r:
            return r.value
        return None

    def arity(self) -> int:
        return len(self.declaration.params)

    def __str__(self):
        return f'<fun {self.declaration.name.lexeme}>'


__all__ = [
    'LoxCallable',
    'LoxClock',
    'lox_clock',
    'LoxFunction',
]
