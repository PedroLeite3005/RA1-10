# Testes do Aluno 3 - lerArquivo e gerarAssembly (versão VFP)

import unittest
import os
import tempfile
from assembly_generator import lerArquivo, gerarAssembly, double_to_words
from lexer import Lexer


class TestLerArquivo(unittest.TestCase):

    def _tmp(self, conteudo):
        fd, path = tempfile.mkstemp(suffix=".txt")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(conteudo)
        return path

    def test_le_arquivo_normal(self):
        p = self._tmp("( 3.14 2.0 + )\n( 10 5 - )\n")
        linhas = []
        self.assertTrue(lerArquivo(p, linhas))
        os.unlink(p)
        self.assertEqual(len(linhas), 2)
        self.assertEqual(linhas[0], "( 3.14 2.0 + )")

    def test_pula_linhas_vazias(self):
        p = self._tmp("( 1 2 + )\n\n\n( 3 4 * )\n")
        linhas = []
        self.assertTrue(lerArquivo(p, linhas))
        os.unlink(p)
        self.assertEqual(len(linhas), 2)

    def test_tira_espacos(self):
        p = self._tmp("  ( 1 2 + )  \n")
        linhas = []
        self.assertTrue(lerArquivo(p, linhas))
        os.unlink(p)
        self.assertEqual(linhas[0], "( 1 2 + )")

    def test_arquivo_nao_existe(self):
        linhas = []
        self.assertFalse(lerArquivo("nao_existe_abc123.txt", linhas))

    def test_arquivo_vazio(self):
        p = self._tmp("")
        linhas = []
        self.assertTrue(lerArquivo(p, linhas))
        os.unlink(p)
        self.assertEqual(len(linhas), 0)

    def test_10_linhas(self):
        conteudo = "\n".join(f"( {i} {i+1} + )" for i in range(10))
        p = self._tmp(conteudo)
        linhas = []
        self.assertTrue(lerArquivo(p, linhas))
        os.unlink(p)
        self.assertEqual(len(linhas), 10)


class TestDoubleToWords(unittest.TestCase):

    def test_zero(self):
        self.assertEqual(double_to_words(0.0), (0, 0))

    def test_um(self):
        hi, lo = double_to_words(1.0)
        self.assertEqual(hi, 0x3FF00000)
        self.assertEqual(lo, 0)

    def test_negativo(self):
        hi, _ = double_to_words(-1.0)
        self.assertEqual(hi, 0xBFF00000)

    def test_decimal(self):
        hi, lo = double_to_words(3.14)
        self.assertNotEqual(hi, 0)
        self.assertNotEqual((hi, lo), (0, 0))


class TestGerarAssembly(unittest.TestCase):

    def _gerar(self, linhas):
        tokens = [Lexer().parseExpressao(l) for l in linhas]
        codigo = []
        gerarAssembly(tokens, codigo)
        return "\n".join(codigo)

    def test_inicio_programa(self):
        asm = self._gerar(["( 3.14 2.0 + )"])
        self.assertIn("_start:", asm)
        self.assertIn(".text", asm)
        self.assertIn(".global _start", asm)

    def test_vfp_habilitado(self):
        asm = self._gerar(["( 1.0 2.0 + )"])
        self.assertIn(".fpu vfpv3", asm)
        self.assertIn(".arch armv7-a", asm)

    def test_soma(self):
        asm = self._gerar(["( 3.14 2.0 + )"])
        self.assertIn("op +", asm)
        self.assertIn("VADD.F64", asm)

    def test_subtracao(self):
        asm = self._gerar(["( 10 3 - )"])
        self.assertIn("op -", asm)
        self.assertIn("VSUB.F64", asm)

    def test_multiplicacao(self):
        asm = self._gerar(["( 4.0 2.5 * )"])
        self.assertIn("op *", asm)
        self.assertIn("VMUL.F64", asm)

    def test_divisao(self):
        asm = self._gerar(["( 9.0 3.0 / )"])
        self.assertIn("op /", asm)
        self.assertIn("VDIV.F64", asm)

    def test_divisao_inteira(self):
        asm = self._gerar(["( 7 3 // )"])
        self.assertIn("op //", asm)
        self.assertIn("_double_div_to_int:", asm)
        self.assertIn("_int_to_double:", asm)

    def test_modulo(self):
        asm = self._gerar(["( 10 3 % )"])
        self.assertIn("op %", asm)
        self.assertIn("_double_mod:", asm)
        self.assertIn("_smod32:", asm)

    def test_potencia(self):
        asm = self._gerar(["( 2.0 3 ^ )"])
        self.assertIn("op ^", asm)
        self.assertIn("_double_pow:", asm)
        self.assertIn("pow_loop_", asm)

    def test_mem_salvar(self):
        asm = self._gerar(["( 42.0 RESULTADO )"])
        self.assertIn("mem_RESULTADO", asm)
        self.assertIn("salvar em RESULTADO", asm)

    def test_mem_ler(self):
        asm = self._gerar(["( RESULTADO )"])
        self.assertIn("mem_RESULTADO", asm)
        self.assertIn("ler RESULTADO", asm)

    def test_res(self):
        asm = self._gerar(["( 10 5 + )", "( 0 RES )"])
        self.assertIn("historico", asm)
        self.assertIn("comando RES", asm)
        self.assertIn("cont_res", asm)

    def test_aninhada(self):
        asm = self._gerar(["( ( 3.0 2.0 + ) ( 4.0 2.0 * ) / )"])
        self.assertIn("op +", asm)
        self.assertIn("op *", asm)
        self.assertIn("op /", asm)

    def test_halt(self):
        asm = self._gerar(["( 1 2 + )"])
        self.assertIn("halt:", asm)
        self.assertIn("B halt", asm)

    def test_leds(self):
        asm = self._gerar(["( 1 2 + )"])
        self.assertIn("0xFF200000", asm)

    def test_hex_display(self):
        asm = self._gerar(["( 1 2 + )"])
        self.assertIn("0xFF200020", asm)
        self.assertIn("tabela_7seg", asm)

    def test_constantes_ieee754(self):
        asm = self._gerar(["( 1.0 2.0 + )"])
        # 1.0 -> hi = 0x3FF00000, low = 0
        # 2.0 -> hi = 0x40000000, low = 0
        self.assertIn("0x3FF00000", asm)
        self.assertIn("0x40000000", asm)

    def test_pilha(self):
        asm = self._gerar(["( 1 2 + )"])
        self.assertIn("topo_pilha", asm)
        self.assertIn("pilha: .space", asm)

    def test_varias_linhas(self):
        asm = self._gerar(["( 1 2 + )", "( 3 4 * )", "( 5 6 - )"])
        self.assertIn("Linha 1", asm)
        self.assertIn("Linha 2", asm)
        self.assertIn("Linha 3", asm)

    def test_helpers_presentes(self):
        asm = self._gerar(["( 1 2 + )"])
        self.assertIn("_double_to_int:", asm)
        self.assertIn("_int_to_double:", asm)
        self.assertIn("_udivmod32:", asm)

    def test_completo(self):
        asm = self._gerar([
            "( 3.14 2.0 + )",
            "( 10.5 3.5 - )",
            "( 4.0 2.5 * )",
            "( 9.0 3.0 / )",
            "( 7 3 // )",
            "( 10 3 % )",
            "( 2.0 3 ^ )",
            "( 0 RES )",
            "( ( 3.0 2.0 + ) ( 4.0 2.0 * ) / )",
            "( 42.0 RESULTADO )",
        ])

        for sub in ["VADD.F64", "VSUB.F64", "VMUL.F64", "VDIV.F64"]:
            self.assertIn(sub, asm)

        for sub in ["_double_div_to_int:", "_double_mod:", "_double_pow:"]:
            self.assertIn(sub, asm)

        self.assertIn("mem_RESULTADO", asm)
        self.assertIn("historico", asm)
        self.assertIn("0xFF200000", asm)
        self.assertIn("0xFF200020", asm)


if __name__ == "__main__":
    unittest.main()
