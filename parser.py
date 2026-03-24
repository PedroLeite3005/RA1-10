from error import ParseError
from tokens import Token, TokenType

RpnAtom = tuple[str, ...]

class TokenStream:
    def __init__(self, tokens: list[Token]) -> None:
        self._tokens = tokens
        self._i = 0

    def peek(self) -> Token | None:
        if self._i >= len(self._tokens):
            return None
        return self._tokens[self._i]

    def next(self) -> Token:
        if self._i >= len(self._tokens):
            raise ParseError("Unexpected end of input.")
        t = self._tokens[self._i]
        self._i += 1
        return t

    def at_end(self) -> bool:
        return self._i >= len(self._tokens)


def _is_open_paren(t: Token) -> bool:
    return t.token_type == TokenType.GROUP and t.lexeme == "("


def _is_close_paren(t: Token) -> bool:
    return t.token_type == TokenType.GROUP and t.lexeme == ")"


def _build_group_rpn(filhos: list[list[RpnAtom]]) -> list[RpnAtom]:
    if len(filhos) == 1:
        f0 = filhos[0]
        if len(f0) == 1 and f0[0][0] == "var":
            return f0
        raise ParseError(
            "Invalid single-element group: expected (VAR) to read a variable."
        )

    if len(filhos) == 2:
        f0, f1 = filhos[0], filhos[1]
        if f1 == [("kw", "RES")]:
            return f0 + [("res",)]
        if len(f1) == 1 and f1[0][0] == "var":
            nome = f1[0][1]
            return f0 + [("store", nome)]
        raise ParseError(
            "Invalid two-element group: expected (N RES) or (expr VAR) for assignment."
        )

    if len(filhos) == 3:
        op_part = filhos[2]
        if len(op_part) != 1 or op_part[0][0] != "op":
            raise ParseError(
                "The last element inside '()' must be an operator for binary postfix."
            )
        op = op_part[0][1]
        return filhos[0] + filhos[1] + [("op", op)]

    raise ParseError("Invalid parenthesized group: wrong number of elements.")


def parse_expression(stream: TokenStream) -> list[RpnAtom]:
    token = stream.next()

    if _is_open_paren(token):
        filhos: list[list[RpnAtom]] = []
        while True:
            p = stream.peek()
            if p is None:
                raise ParseError("Expected ')' before end of input.")
            if _is_close_paren(p):
                break
            filhos.append(parse_expression(stream))

        stream.next()  # consume ")"

        if not filhos:
            raise ParseError("Empty group '()' is not allowed.")

        return _build_group_rpn(filhos)

    if token.token_type == TokenType.NUMBER:
        return [("num", token.lexeme)]

    if token.token_type == TokenType.OPERATOR:
        return [("op", token.lexeme)]

    if token.token_type == TokenType.IDENT:
        return [("var", token.lexeme)]

    if token.token_type == TokenType.KEYWORD:
        return [("kw", token.lexeme)]

    raise ParseError(f"Unexpected token: {token!r}.")


def parse(tokens: list[Token]) -> list[RpnAtom]:
    if not tokens:
        raise ParseError("No tokens to parse.")

    stream = TokenStream(tokens)
    first = stream.peek()
    assert first is not None

    if _is_open_paren(first):
        rpn = parse_expression(stream)
        if not stream.at_end():
            raise ParseError("Extra tokens after the main expression.")
        return rpn

    raise ParseError("RPN expressions must be surrounded by parenthesis.")
