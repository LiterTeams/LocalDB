class ConstantError(Exception):

    def __init__(self, constant, message="You are trying to change an immutable variable!"):
        self.constant = constant
        self.message = message + f":[{self.constant}]"
        super().__init__(self.message)


class KeyDuplicateError(Exception):

    def __init__(self, key, message="Duplicate key found!"):
        self.key = key
        self.message = message + f":[{self.key}]"
        super().__init__(self.message)


class KeyNull(Exception):

    def __init__(self, key, message="NullebleKey key!"):
        self.key = key
        self.message = message + f":[{self.key}]"
        super().__init__(self.message)

