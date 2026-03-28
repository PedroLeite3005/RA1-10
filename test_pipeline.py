import io
import unittest
from unittest.mock import patch

from main import exibir_resultados, processar_linhas


class TestProcessarLinhas(unittest.TestCase):
    def test_mem_assign_and_read(self):
        linhas = ["( 42 MEM )", "( MEM )"]
        r = processar_linhas(linhas)
        self.assertEqual(len(r), 2)
        self.assertAlmostEqual(r[0], 42.0)
        self.assertAlmostEqual(r[1], 42.0)

    def test_mem_from_variable(self):
        linhas = ["( 5 A )", "( A MEM )", "( MEM )"]
        r = processar_linhas(linhas)
        self.assertAlmostEqual(r[0], 5.0)
        self.assertAlmostEqual(r[1], 5.0)
        self.assertAlmostEqual(r[2], 5.0)

    def test_res_after_two_expressions(self):
        linhas = ["( 10 5 + )", "( 100 1 + )", "( 1 RES )"]
        r = processar_linhas(linhas)
        self.assertAlmostEqual(r[0], 15.0)
        self.assertAlmostEqual(r[1], 101.0)
        self.assertAlmostEqual(r[2], 15.0)

    def test_nested_expression(self):
        linhas = ["( ( 3.0 2.0 + ) ( 4.0 2.0 * ) / )"]
        r = processar_linhas(linhas)
        self.assertAlmostEqual(r[0], 5.0 / 8.0)


class TestExibirResultados(unittest.TestCase):
    def test_one_decimal_per_line(self):
        buf = io.StringIO()
        with patch("sys.stdout", buf):
            exibir_resultados([42.0, 3.14])
        self.assertEqual(buf.getvalue(), "42.0\n3.1\n")


if __name__ == "__main__":
    unittest.main()
