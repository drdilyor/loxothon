from lox.token import Token


class LoxRuntimeError(Exception):
    def __init__(self, token: Token, message: str):
        self.token = token
        self.message = message
        super().__init__(message)


__all__ = ['LoxRuntimeError']