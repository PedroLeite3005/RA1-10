class InvalidTokenException(Exception):
    def __init__(self, lexeme):
        super().__init__(f"Invalid token '{lexeme}' found on source code.")


class InvalidNumberException(Exception):
    def __init__(self, lexeme):
        super().__init__(f"Invalid number literal '{lexeme}': multiple decimal points are not allowed.")


class LowerCaseException(Exception):
    def __init__(self, lexeme):
        super().__init__(f"Identifiers and keywords can only have uppercase keywords. Found '{lexeme}'")
