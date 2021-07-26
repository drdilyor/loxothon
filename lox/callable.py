import time
from abc import ABC, abstractmethod

import lox
import lox.stmt as stmt


class LoxCallable(ABC):
    @abstractmethod
    def call(self, interpreter: 'lox.Interpreter', arguments: list) -> object:
        ...  # pragma: no cover

    @abstractmethod
    def arity(self) -> int: ...


class LoxClock(LoxCallable):
    def call(self, interpreter: 'lox.Interpreter', arguments: list) -> object:
        return time.time()

    def arity(self) -> int:
        return 0

    def __str__(self):
        return '<native fun>'


lox_clock = LoxClock()


class LoxFunction(LoxCallable):
    def __init__(self, declaration: stmt.Function,
                 closure: 'lox.Environment',
                 is_init=False):
        self.declaration = declaration
        self.closure = closure
        self.is_init = is_init
        assert not (is_init and declaration.is_getter), \
            "Cannot be init and getter at the same time."

    def __str__(self):
        return f'<fun {self.declaration.name.lexeme}>'

    @property
    def is_getter(self):
        return self.declaration.is_getter

    @property
    def is_setter(self):
        # this is actually unused
        return self.declaration.is_setter  # pragma: no cover

    def call(self, interpreter: 'lox.Interpreter', arguments: list) -> object:
        environment = lox.Environment(self.closure)
        for param, argument in zip(self.declaration.params, arguments):
            environment.define(param.lexeme, argument)

        try:
            interpreter.execute_block(self.declaration.body, environment)
        except lox.LoxReturn as r:
            if self.is_init:
                return self.closure.get_at(0, 'this')
            return r.value
        if self.is_init:
            return self.closure.get_at(0, 'this')
        return None

    def arity(self) -> int:
        return len(self.declaration.params)

    def bind(self, instance):
        environment = lox.Environment(self.closure)
        environment.define('this', instance)
        return LoxFunction(self.declaration, environment, self.is_init)


__all__ = [
    'LoxCallable',
    'LoxClock',
    'lox_clock',
    'LoxFunction',
]
