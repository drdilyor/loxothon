from typing import Dict, Optional
import lox


class LoxInstance:
    def __init__(self, class_: 'LoxClass'):
        self.class_ = class_
        self.fields: dict[str, object] = {}
        self.getters: dict[str, lox.LoxCallable] = {}

    def __str__(self):
        return f'<instance {self.class_.name}>'

    def get(self, name: 'lox.Token', interpreter: 'lox.Interpreter'):
        if name.lexeme in self.fields:
            return self.fields[name.lexeme]
        method = self.class_.find_method(name.lexeme)
        if method:
            return method.bind(self)

        getter = self.class_.find_getter(name.lexeme)
        if getter:
            return getter.bind(self).call(interpreter, [])

        raise lox.LoxRuntimeError(name, f"Undefined property '{name.lexeme}'.")

    def set(self, name: 'lox.Token', value: object):
        self.fields[name.lexeme] = value


class LoxClass(LoxInstance, lox.LoxCallable):
    def __init__(self,
                 metaclass: Optional['LoxClass'],
                 name: str,
                 methods: Dict[str, 'lox.LoxFunction'],
                 getters: Dict[str, 'lox.LoxFunction']):
        super().__init__(metaclass)
        self.name = name
        self.methods = methods
        self.getters = getters

    def __str__(self):
        return f'<class {self.name}>'

    def call(self, interpreter: 'lox.Interpreter', arguments: list) -> object:
        instance = LoxInstance(self)
        initializer = self.find_method('init')
        if initializer:
            initializer.bind(instance).call(interpreter, arguments)

        return instance

    def find_method(self, name: str):
        return self.methods.get(name)

    def find_getter(self, name: str) -> lox.LoxFunction:
        return self.getters[name]

    def arity(self) -> int:
        initializer = self.find_method('init')
        if not initializer:
            return 0
        return initializer.arity()


__all__ = [
    'LoxClass',
    'LoxInstance',
]
