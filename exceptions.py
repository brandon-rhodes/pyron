"""Exception class for Pyron error messages."""

class PyronError(Exception):
    def __init__(self, message, error_code=1):
        Exception.__init__(self, message)
        self.error_code = error_code
