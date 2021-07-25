from typing import Dict, Optional
import lox


class LoxInstance:
    def __init__(self, class_: 'LoxClass'):
        self.class_ = class_
        self.fields: dict[str, object] = {}

    def __str__(self):
        return f'<instance {self.class_.name}>'

    def get(self, name: 'lox.Token', interpreter: 'lox.Interpreter'):
        if name.lexeme in self.fields:
            return self.fields[name.lexeme]
        method = self.class_.find_method(name.lexeme)
        if method:
            result = method.bind(self)
            if method.is_getter:
                result = result.call(interpreter, [])
            return result

        raise lox.LoxRuntimeError(name, f"Undefined property '{name.lexeme}'.")

    def set(self,
            name: 'lox.Token',
            value: object,
            interepreter: 'lox.Interpreter'):
        setter = self.class_.find_setter(name.lexeme)
        if setter:
            # There cannot be a field named the same as setter
            # because setter will be called when setting such a field
            assert name.lexeme not in self.fields
            setter.bind(self).call(interepreter, [value])

        else:
            self.fields[name.lexeme] = value


class LoxClass(LoxInstance, lox.LoxCallable):
    def __init__(self,
                 metaclass: Optional['LoxClass'],
                 name: str,
                 methods: Dict[str, 'lox.LoxFunction'],
                 setters: Dict[str, 'lox.LoxFunction']):
        super().__init__(metaclass)
        self.name = name
        self.methods = methods
        self.setters = setters

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

    def find_setter(self, name: str):
        return self.setters.get(name)

    def arity(self) -> int:
        initializer = self.find_method('init')
        if not initializer:
            return 0
        return initializer.arity()


__all__ = [
    'LoxClass',
    'LoxInstance',
]
