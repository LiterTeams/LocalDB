class NotFoundError(Exception):
    def __init__(self, value, function_name, message="Code Status: 404"):
        self.message = f"{message} | Function: {function_name} | Value: {value}"
        super().__init__(self.message)


class NotAcceptableError(Exception):
    def __init__(self, value, function_name, message="Code Status: 406"):
        self.message = f"{message} | Function: {function_name} | Value: {value}"
        super().__init__(self.message)


class DuplicateError(Exception):
    def __init__(self, value, function_name, message="Code Status: 432"):
        self.message = f"{message} | Function: {function_name} | Value: {value}"
        super().__init__(self.message)


class InitializationError(Exception):
    def __init__(self, value, function_name, message="Code Status: 528"):
        self.message = f"{message} | Function: {function_name} | Value: {value}"
        super().__init__(self.message)


class NoContentError(Exception):
    def __init__(self, value, function_name, message="Code Status: 529"):
        self.message = f"{message} | Function: {function_name} | Value: {value}"
        super().__init__(self.message)
