from tokens import Token, TokenType
from error import LowerCaseException, InvalidNumberException, InvalidTokenException

class Lexer:
    tokens: list[Token]
    idx: int
    input: str

    def __init__(self):
        self.idx = 0 
        self.tokens = [] 

    
    def parseExpressao(self, line: str) -> list[Token]:
        self.input = line.strip()
        while self.idx_is_valid():
            current_char = self.get_char()
            match current_char:
                case "(" | ")":
                    self.state_parenthesis()
                case "+" | "*" | "%" | "-" | "/" | "^":
                    self.state_operator()
                case char if char.isdigit():
                    self.state_number()
                case char if char.isupper():
                    self.state_identifier()
                case " ":
                    self.state_space()
                case char if char.islower():
                    raise LowerCaseException(self.get_char())
                case _:
                    raise InvalidTokenException(self.get_char())

        result = self.tokens.copy()
        self.tokens.clear()
        self.idx = 0
        self.input = ""
        return result

    def state_parenthesis(self):
        parenthesis_token = Token(TokenType.GROUP, self.consume_char())
        self.tokens.append(parenthesis_token)

    def state_operator(self):
        operator_token = Token(TokenType.OPERATOR, self.consume_char())
        self.tokens.append(operator_token)

    def state_number(self):
        buffer = ""
        while self.idx_is_valid() and (self.get_char().isdigit() or self.get_char() == "."):
            buffer += self.consume_char()

        if buffer.count(".") > 1:
            raise InvalidNumberException(buffer)

        token = Token(TokenType.NUMBER, buffer)
        self.tokens.append(token)

    def state_identifier(self):
        buffer = ""
        while self.idx_is_valid() and self.get_char().isupper():
            buffer += self.consume_char()

        if buffer == "RES":
            self.state_keyword()
            return

        token = Token(TokenType.IDENT, buffer)
        self.tokens.append(token)

    def state_keyword(self):
        token = Token(TokenType.KEYWORD, "RES")
        self.tokens.append(token)

    def state_space(self):
        self.consume_char()
        
    def get_char(self) -> str:
        return self.input[self.idx]

    def consume_char(self) -> str:
        char = self.get_char()
        self.idx += 1
        return char

    def idx_is_valid(self):
        return self.idx < len(self.input)


