import unittest

from lexer import Lexer
from tokens import TokenType
from error import LowerCaseException, InvalidNumberException, InvalidTokenException


class TestLexer(unittest.TestCase):
    def setUp(self):
        self.lexer = Lexer()

    def assert_token(self, token, expected_type, expected_lexeme):
        self.assertEqual(token.token_type, expected_type)
        self.assertEqual(token.lexeme, expected_lexeme)

    # Testes para parseExpressao
    def test_single_number(self):
        tokens = self.lexer.parseExpressao("123")
        self.assertEqual(len(tokens), 1)
        self.assert_token(tokens[0], TokenType.NUMBER, "123")

    def test_decimal_number(self):
        tokens = self.lexer.parseExpressao("10.5")
        self.assertEqual(len(tokens), 1)
        self.assert_token(tokens[0], TokenType.NUMBER, "10.5")

    def test_identifier(self):
        tokens = self.lexer.parseExpressao("VARINHA")
        self.assertEqual(len(tokens), 1)
        self.assert_token(tokens[0], TokenType.IDENT, "VARINHA")

    def test_keyword_res(self):
        tokens = self.lexer.parseExpressao("RES")
        self.assertEqual(len(tokens), 1)
        self.assert_token(tokens[0], TokenType.KEYWORD, "RES")

    def test_operator(self):
        tokens = self.lexer.parseExpressao("+")
        self.assertEqual(len(tokens), 1)
        self.assert_token(tokens[0], TokenType.OPERATOR, "+")

    def test_parenthesis(self):
        tokens = self.lexer.parseExpressao("( )")
        self.assertEqual(len(tokens), 2)
        self.assert_token(tokens[0], TokenType.GROUP, "(")
        self.assert_token(tokens[1], TokenType.GROUP, ")")

    def test_ignores_spaces(self):
        tokens = self.lexer.parseExpressao("  10   ABC   +   ")
        self.assertEqual(len(tokens), 3)
        self.assert_token(tokens[0], TokenType.NUMBER, "10")
        self.assert_token(tokens[1], TokenType.IDENT, "ABC")
        self.assert_token(tokens[2], TokenType.OPERATOR, "+")

    def test_complete_expression(self):
        tokens = self.lexer.parseExpressao("10 VARINHA + RES ( 2.5 )")
        self.assertEqual(len(tokens), 7)

        expected = [
            (TokenType.NUMBER, "10"),
            (TokenType.IDENT, "VARINHA"),
            (TokenType.OPERATOR, "+"),
            (TokenType.KEYWORD, "RES"),
            (TokenType.GROUP, "("),
            (TokenType.NUMBER, "2.5"),
            (TokenType.GROUP, ")"),
        ]

        for token, (expected_type, expected_lexeme) in zip(tokens, expected):
            self.assert_token(token, expected_type, expected_lexeme)

    def test_raises_lowercase_exception(self):
        with self.assertRaises(LowerCaseException):
            self.lexer.parseExpressao("abc")

    def test_raises_invalid_token_exception(self):
        with self.assertRaises(InvalidTokenException):
            self.lexer.parseExpressao("@")

    def test_raises_invalid_number_exception(self):
        with self.assertRaises(InvalidNumberException):
            self.lexer.parseExpressao("12.3.4")

    def test_state_is_reset_between_calls(self):
        tokens1 = self.lexer.parseExpressao("123")
        tokens2 = self.lexer.parseExpressao("ABC")

        self.assertEqual(len(tokens1), 1)
        self.assertEqual(len(tokens2), 1)

        self.assert_token(tokens1[0], TokenType.NUMBER, "123")
        self.assert_token(tokens2[0], TokenType.IDENT, "ABC")


if __name__ == "__main__":
    unittest.main()
