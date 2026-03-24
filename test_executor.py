import unittest

from executor import ContextoExecucao
from lexer import Lexer
from parser import parse


def _eval_with_mem(line: str, memoria: dict[str, float]) -> float:
    ctx = ContextoExecucao()
    ctx.memoria.update(memoria)
    tokens = Lexer().parseExpressao(line)
    rpn = parse(tokens)
    return ctx.executar_raiz(rpn)


class TestExecutarExpressao(unittest.TestCase):
    # (A (C D *) +): A + (C * D)
    def test_sum_a_with_product_c_d(self):
        line = "( A ( C D * ) + )"
        r = _eval_with_mem(line, {"A": 2.0, "C": 3.0, "D": 4.0})
        self.assertAlmostEqual(r, 14.0)

    # ((A B *) (D E *) /): (A*B) / (D*E)
    def test_divide_product_ab_by_product_de(self):
        line = "( ( A B * ) ( D E * ) / )"
        r = _eval_with_mem(line, {"A": 6.0, "B": 4.0, "D": 2.0, "E": 3.0})
        self.assertAlmostEqual(r, 4.0)

    # ((A B +) (C D *) /): (A+B) / (C*D)
    def test_divide_sum_ab_by_product_cd(self):
        line = "( ( A B + ) ( C D * ) / )"
        r = _eval_with_mem(line, {"A": 1.0, "B": 2.0, "C": 3.0, "D": 4.0})
        self.assertAlmostEqual(r, 0.25)

    def test_nested_with_numbers_only(self):
        r = _eval_with_mem("( ( 3.0 2.0 + ) ( 4.0 2.0 * ) / )", {})
        self.assertAlmostEqual(r, 5.0 / 8.0)

    def test_mem_read_and_assign(self):
        # 42 MEM = 42
        # MEM = 42
        ctx = ContextoExecucao()
        lexer = Lexer()
        ctx.executar_raiz(parse(lexer.parseExpressao("( 42 MEM )")))
        self.assertEqual(ctx.memoria.get("MEM"), 42.0)
        r = ctx.executar_raiz(parse(lexer.parseExpressao("( MEM )")))
        self.assertEqual(r, 42.0)

    def test_res_history(self):
        # 10 5 = 15
        # 100 1 = 101
        # 1 RES = 15
        ctx = ContextoExecucao()
        lexer = Lexer()
        ctx.executar_raiz(parse(lexer.parseExpressao("( 10 5 + )")))
        ctx.executar_raiz(parse(lexer.parseExpressao("( 100 1 + )")))
        r = ctx.executar_raiz(parse(lexer.parseExpressao("( 1 RES )")))
        self.assertAlmostEqual(r, 15.0)


if __name__ == "__main__":
    unittest.main()
