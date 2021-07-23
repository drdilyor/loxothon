from abc import ABC, abstractmethod
import time


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


__all__ = ['LoxCallable', 'LoxClock']
