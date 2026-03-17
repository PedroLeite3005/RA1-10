from enum import Enum, auto

class TokenType(Enum):
    IDENT = auto()
    KEYWORD = auto()
    NUMBER= auto()
    OPERATOR = auto()
    GROUP = auto()

class Token:
    token_type : TokenType
    lexeme : str

    def __init__(self,token_type: TokenType, lexeme: str):
        self.token_type = token_type
        self.lexeme = lexeme

    def __repr__(self):
        return f"Token(type={self.token_type}, lexeme='{self.lexeme}')"
