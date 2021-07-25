from typing import Dict
import lox

class LoxClass(lox.LoxCallable):
    def __init__(self, name: 'lox.Token', methods: Dict[str, 'lox.LoxFunction']):
        self.name = name
        self.methods = methods

    def __str__(self):
        return f'<class {self.name.lexeme}>'

    def call(self, interpreter: 'lox.Interpreter', arguments: list) -> object:
        instance = LoxInstance(self)
        initializer = self.find_method('init')
        if initializer:
            initializer.bind(instance).call(interpreter, arguments)

        return instance

    def find_method(self, name: str):
        return self.methods.get(name)

    def arity(self) -> int:
        initializer = self.find_method('init')
        if not initializer:
            return 0
        return initializer.arity()


class LoxInstance:
    def __init__(self, class_: LoxClass):
        self.class_ = class_
        self.fields: dict[str, object] = {}

    def __str__(self):
        return f'<instance {self.class_.name.lexeme}>'

    def get(self, name: 'lox.Token'):
        if name.lexeme in self.fields:
            return self.fields[name.lexeme]
        method = self.class_.find_method(name.lexeme)
        if method:
            return method.bind(self)

        raise lox.LoxRuntimeError(name, f"Undefined property '{name.lexeme}'.")

    def set(self, name: 'lox.Token', value: object):
        self.fields[name.lexeme] = value


__all__ = [
    'LoxClass',
    'LoxInstance',
]
