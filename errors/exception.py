"""Registry for all Exceptions

This module contains all the exceptions that can be raised
in the application
Custom Exceptions are defined here
"""

class AuthException(Exception):
    """
    Raise All Exceptions relating to authentication
    and authorization
    """

    def __init__(self, msg, code=None):
        self.msg = msg
        self.code = code



class InternalProcessingError(Exception):
    """
    Raise All Exceptions relating to internal
    Processing Error
    """

    def __init__(self, msg, code=None):
        self.msg = msg
        self.code = code