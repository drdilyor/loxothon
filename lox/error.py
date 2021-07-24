import lox


class LoxRuntimeError(Exception):
    def __init__(self, token: 'lox.Token', message: str):
        self.token = token
        self.message = message
        super().__init__(message)


class LoxStopIteration(Exception):
    pass


class LoxReturn(Exception):
    def __init__(self, value):
        super().__init__()
        self.value = value


__all__ = ['LoxRuntimeError', 'LoxStopIteration', 'LoxReturn']
