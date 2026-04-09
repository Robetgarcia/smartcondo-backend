"""
Exceções customizadas
"""

class SmartCondoException(Exception):
    pass

class ValidationError(SmartCondoException):
    pass

class DatabaseError(SmartCondoException):
    pass

class AuthenticationError(SmartCondoException):
    pass

class NotFoundError(SmartCondoException):
    pass

class DuplicateError(SmartCondoException):
    pass
