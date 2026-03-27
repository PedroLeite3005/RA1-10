# Aluno 3 - Pedro Bastos Leite (PedroLeite3005)
# lerArquivo e gerarAssembly - Assembly ARMv7 pro CPUlator DE1-SoC
# Versão refeita para usar VFP/double IEEE-754 em vez de soft-float artesanal.

from __future__ import annotations

import struct
from parser import parse


def lerArquivo(nomeArquivo: str, linhas: list[str]) -> bool:
    try:
        with open(nomeArquivo, "r", encoding="utf-8") as arq:
            for linha_bruta in arq:
                linha = linha_bruta.strip()
                if linha:
                    linhas.append(linha)
        return True
    except FileNotFoundError:
        print(f"Erro: arquivo '{nomeArquivo}' não encontrado.")
        return False
    except IOError as erro:
        print(f"Erro ao ler '{nomeArquivo}': {erro}")
        return False


def double_to_words(valor: float) -> tuple[int, int]:
    """
    Retorna (hi, lo) do double em IEEE-754.
    """
    raw = struct.pack(">d", valor)
    hi = int.from_bytes(raw[0:4], "big")
    lo = int.from_bytes(raw[4:8], "big")
    return hi, lo


def _hex32(val: int) -> str:
    return f"0x{val & 0xFFFFFFFF:08X}"


class _Gerador:
    """
    Convenção interna do gerador:
      - double em registradores ARM: R0 = low, R1 = high
      - double em memória:       [addr] = low, [addr+4] = high

    Isso permite usar: VMOV Dn, R0, R1
    """

    def __init__(self) -> None:
        self.asm: list[str] = []
        self.dados: list[str] = []
        self.num_labels = 0
        self.num_consts = 0
        self.consts_criadas: dict[str, str] = {}
        self.vars_usadas: set[str] = set()

    def _label(self, prefixo: str = "L") -> str:
        self.num_labels += 1
        return f"{prefixo}_{self.num_labels}"

    def _const_double(self, valor: float) -> str:
        chave = struct.pack(">d", valor).hex()
        if chave in self.consts_criadas:
            return self.consts_criadas[chave]

        self.num_consts += 1
        nome = f"dbl_{self.num_consts}"
        self.consts_criadas[chave] = nome

        hi, lo = double_to_words(valor)
        self.dados.append(f"{nome}:")
        self.dados.append(f"    .word {_hex32(lo)}")
        self.dados.append(f"    .word {_hex32(hi)}")
        return nome

    def _ltorg(self) -> None:
        lbl = self._label("skip")
        self.asm.append(f"    B {lbl}")
        self.asm.append("    .ltorg")
        self.asm.append(f"{lbl}:")

    def _push01(self) -> None:
        self.asm.append("    PUSH {R1}")
        self.asm.append("    PUSH {R0}")

    def _pop01(self) -> None:
        self.asm.append("    POP {R0}")
        self.asm.append("    POP {R1}")

    def _pop23(self) -> None:
        self.asm.append("    POP {R2}")
        self.asm.append("    POP {R3}")

    def _push_label(self, label: str) -> None:
        self.asm.append(f"    LDR R4, ={label}")
        self.asm.append("    LDR R0, [R4]")
        self.asm.append("    LDR R1, [R4, #4]")
        self._push01()

    def _numero(self, txt: str) -> None:
        label = self._const_double(float(txt))
        self.asm.append(f"    @ empilha {txt}")
        self._push_label(label)

    def _ler_var(self, nome: str) -> None:
        self.vars_usadas.add(nome)
        self.asm.append(f"    @ ler {nome}")
        self._push_label(f"mem_{nome}")

    def _salvar_var(self, nome: str) -> None:
        self.vars_usadas.add(nome)
        self.asm.append(f"    @ salvar em {nome}")
        self.asm.append("    LDR R0, [SP]")
        self.asm.append("    LDR R1, [SP, #4]")
        self.asm.append(f"    LDR R4, =mem_{nome}")
        self.asm.append("    STR R0, [R4]")
        self.asm.append("    STR R1, [R4, #4]")

    def _op_bin_vfp(self, instr: str) -> None:
        self._pop23()  # b
        self._pop01()  # a
        self.asm.append("    VMOV D0, R0, R1")
        self.asm.append("    VMOV D1, R2, R3")
        self.asm.append(f"    {instr} D0, D0, D1")
        self.asm.append("    VMOV R0, R1, D0")
        self._push01()

    def _operacao(self, op: str) -> None:
        self.asm.append(f"    @ op {op}")

        if op == "+":
            self._op_bin_vfp("VADD.F64")
            return
        if op == "-":
            self._op_bin_vfp("VSUB.F64")
            return
        if op == "*":
            self._op_bin_vfp("VMUL.F64")
            return
        if op == "/":
            self._op_bin_vfp("VDIV.F64")
            return

        self._pop23()  # b
        self._pop01()  # a

        if op == "//":
            self.asm.append("    BL _double_div_to_int")
            self.asm.append("    BL _int_to_double")
            self._push01()
            return

        if op == "%":
            self.asm.append("    BL _double_mod")
            self._push01()
            return

        if op == "^":
            self.asm.append("    BL _double_pow")
            self._push01()
            return

        raise ValueError(f"Operador desconhecido no gerador: {op!r}")

    def _res(self) -> None:
        self.asm.append("    @ comando RES")
        self._pop01()
        self.asm.append("    BL _double_to_int")
        self.asm.append("    MOV R4, R0")
        self.asm.append("    LDR R5, =cont_res")
        self.asm.append("    LDR R5, [R5]")
        self.asm.append("    SUB R5, R5, #1")
        self.asm.append("    SUB R5, R5, R4")
        self.asm.append("    LDR R6, =historico")
        self.asm.append("    LSL R5, R5, #3")
        self.asm.append("    ADD R6, R6, R5")
        self.asm.append("    LDR R0, [R6]")
        self.asm.append("    LDR R1, [R6, #4]")
        self._push01()

    def _processar(self, rpn) -> None:
        for atomo in rpn:
            t = atomo[0]
            if t == "num":
                self._numero(atomo[1])
            elif t == "var":
                self._ler_var(atomo[1])
            elif t == "op":
                self._operacao(atomo[1])
            elif t == "res":
                self._res()
            elif t == "store":
                self._salvar_var(atomo[1])

    def _seg7_inline(self) -> None:
        self.asm.append("    @ atualiza HEX3..HEX0 com o valor inteiro em R0")
        self.asm.append("    PUSH {R0, R1, R2, R4, R5, R6, R7}")
        self.asm.append("    LDR R4, =0xFF200020")
        self.asm.append("    LDR R5, =tabela_7seg")
        self.asm.append("    MOV R6, R0")
        self.asm.append("    MOV R7, #0")
        for i in range(4):
            self.asm.append("    AND R1, R6, #0xF")
            self.asm.append("    LDRB R2, [R5, R1]")
            if i > 0:
                self.asm.append(f"    LSL R2, R2, #{i * 8}")
            self.asm.append("    ORR R7, R7, R2")
            if i < 3:
                self.asm.append("    LSR R6, R6, #4")
        self.asm.append("    STR R7, [R4]")
        self.asm.append("    POP {R0, R1, R2, R4, R5, R6, R7}")

    def _guardar(self, idx: int) -> None:
        self.asm.append(f"    @ resultado linha {idx}")
        self._pop01()
        self.asm.append("    LDR R4, =historico")
        self.asm.append("    LDR R5, =cont_res")
        self.asm.append("    LDR R6, [R5]")
        self.asm.append("    LSL R7, R6, #3")
        self.asm.append("    ADD R4, R4, R7")
        self.asm.append("    STR R0, [R4]")
        self.asm.append("    STR R1, [R4, #4]")
        self.asm.append("    ADD R6, R6, #1")
        self.asm.append("    STR R6, [R5]")
        self.asm.append("    BL _double_to_int")
        self.asm.append("    LDR R4, =0xFF200000")
        self.asm.append("    STR R0, [R4]")
        self._seg7_inline()
        self.asm.append("")

    def _emit_helpers(self) -> None:
        a = self.asm.append

        a("@ ===== helpers =====")
        a("")

        a("@ R0/R1 = double -> R0 = int32")
        a("_double_to_int:")
        a("    VMOV D0, R0, R1")
        a("    VCVT.S32.F64 S0, D0")
        a("    VMOV R0, S0")
        a("    BX LR")
        a("")

        a("@ R0 = int32 -> R0/R1 = double")
        a("_int_to_double:")
        a("    VMOV S0, R0")
        a("    VCVT.F64.S32 D0, S0")
        a("    VMOV R0, R1, D0")
        a("    BX LR")
        a("")

        a("@ entrada: R0/R1 = a, R2/R3 = b")
        a("@ saída: R0 = int(a / b)")
        a("_double_div_to_int:")
        a("    VMOV D0, R0, R1")
        a("    VMOV D1, R2, R3")
        a("    VDIV.F64 D0, D0, D1")
        a("    VCVT.S32.F64 S0, D0")
        a("    VMOV R0, S0")
        a("    BX LR")
        a("")

        a("@ entrada: R0/R1 = a, R2/R3 = b")
        a("@ saída: R0/R1 = double(int(a) % int(b))")
        a("_double_mod:")
        a("    PUSH {R4-R7, LR}")
        a("    VMOV D0, R0, R1")
        a("    VMOV D1, R2, R3")
        a("    VCVT.S32.F64 S0, D0")
        a("    VCVT.S32.F64 S1, D1")
        a("    VMOV R4, S0")
        a("    VMOV R5, S1")
        a("    MOV R0, R4")
        a("    MOV R1, R5")
        a("    BL _smod32")
        a("    BL _int_to_double")
        a("    POP {R4-R7, PC}")
        a("")

        um = self._const_double(1.0)
        lbl_neg = self._label("pow_neg")
        lbl_loop = self._label("pow_loop")
        lbl_fim = self._label("pow_fim")
        lbl_inv = self._label("pow_inv")
        lbl_done = self._label("pow_done")

        a("@ entrada: R0/R1 = base, R2/R3 = expoente")
        a("@ saída: R0/R1 = base ^ int(expoente)")
        a("_double_pow:")
        a("    PUSH {R4-R8, LR}")
        a("    MOV R4, R0")
        a("    MOV R5, R1")
        a("    VMOV D1, R2, R3")
        a("    VCVT.S32.F64 S0, D1")
        a("    VMOV R6, S0")
        a(f"    LDR R7, ={um}")
        a("    LDR R0, [R7]")
        a("    LDR R1, [R7, #4]")
        a("    MOV R8, #0")
        a("    CMP R6, #0")
        a(f"    BLT {lbl_neg}")
        a(f"    B {lbl_loop}")
        a(f"{lbl_neg}:")
        a("    RSB R6, R6, #0")
        a("    MOV R8, #1")
        a(f"    B {lbl_loop}")
        a(f"{lbl_loop}:")
        a("    CMP R6, #0")
        a(f"    BEQ {lbl_fim}")
        a("    VMOV D0, R0, R1")
        a("    VMOV D1, R4, R5")
        a("    VMUL.F64 D0, D0, D1")
        a("    VMOV R0, R1, D0")
        a("    SUB R6, R6, #1")
        a(f"    B {lbl_loop}")
        a(f"{lbl_fim}:")
        a("    CMP R8, #1")
        a(f"    BEQ {lbl_inv}")
        a(f"    B {lbl_done}")
        a(f"{lbl_inv}:")
        a(f"    LDR R7, ={um}")
        a("    LDR R2, [R7]")
        a("    LDR R3, [R7, #4]")
        a("    VMOV D0, R2, R3")
        a("    VMOV D1, R0, R1")
        a("    VDIV.F64 D0, D0, D1")
        a("    VMOV R0, R1, D0")
        a(f"{lbl_done}:")
        a("    POP {R4-R8, PC}")
        a("")

        a("@ unsigned division/mod: R0=numerador, R1=denominador -> R0=quociente, R1=resto")
        a("_udivmod32:")
        a("    PUSH {R2-R7, LR}")
        a("    MOV R2, #0")
        a("    MOV R3, #0")
        a("    MOV R4, #32")
        a("_udivmod32_loop:")
        a("    LSL R3, R3, #1")
        a("    ORR R3, R3, R0, LSR #31")
        a("    LSL R0, R0, #1")
        a("    CMP R3, R1")
        a("    SUBCS R3, R3, R1")
        a("    ADC R2, R2, R2")
        a("    SUBS R4, R4, #1")
        a("    BNE _udivmod32_loop")
        a("    MOV R0, R2")
        a("    MOV R1, R3")
        a("    POP {R2-R7, PC}")
        a("")

        a("@ signed modulo: R0=a, R1=b -> R0=a%b com sinal de a")
        a("_smod32:")
        a("    PUSH {R2-R7, LR}")
        a("    MOV R3, #0")
        a("    CMP R0, #0")
        a("    RSBMI R0, R0, #0")
        a("    MOVMI R3, #1")
        a("    CMP R1, #0")
        a("    RSBMI R1, R1, #0")
        a("    BL _udivmod32")
        a("    MOV R0, R1")
        a("    CMP R3, #0")
        a("    RSBNE R0, R0, #0")
        a("    POP {R2-R7, PC}")
        a("")

    def montar(self, todos_tokens) -> list[str]:
        self.asm.append("@ Assembly ARMv7 - compilador RPN")
        self.asm.append("@ CPUlator DE1-SoC - versão com VFP/double")
        self.asm.append(".syntax unified")
        self.asm.append(".arch armv7-a")
        self.asm.append(".fpu vfpv3")
        self.asm.append(".global _start")
        self.asm.append(".text")
        self.asm.append("")
        self.asm.append("_start:")
        self.asm.append("    LDR SP, =topo_pilha")
        self.asm.append("    MOV R0, #0")
        self.asm.append("    LDR R1, =cont_res")
        self.asm.append("    STR R0, [R1]")
        self._ltorg()
        self.asm.append("")

        for i, tokens in enumerate(todos_tokens):
            self.asm.append(f"@ -- Linha {i + 1} --")
            rpn = parse(tokens)
            self._processar(rpn)
            self._guardar(i)
            self._ltorg()
            self.asm.append("")

        self.asm.append("halt:")
        self.asm.append("    B halt")
        self.asm.append("")
        self.asm.append("    .ltorg")
        self.asm.append("")

        self._emit_helpers()

        self.asm.append("")
        self.asm.append(".data")
        self.asm.append("")
        self.asm.append("tabela_7seg:")
        seg = [
            0x3F, 0x06, 0x5B, 0x4F,
            0x66, 0x6D, 0x7D, 0x07,
            0x7F, 0x6F, 0x77, 0x7C,
            0x39, 0x5E, 0x79, 0x71,
        ]
        self.asm.append("    .byte " + ", ".join(f"0x{s:02X}" for s in seg))
        self.asm.append("    .align 3")
        self.asm.append("")

        for linha in self.dados:
            self.asm.append(linha)
        self.asm.append("")

        tam = max(len(todos_tokens) + 10, 64)
        self.asm.append("cont_res: .word 0")
        self.asm.append("historico:")
        self.asm.append(f"    .space {tam * 8}")
        self.asm.append("")

        for v in sorted(self.vars_usadas):
            self.asm.append(f"mem_{v}: .word 0, 0")
        self.asm.append("")

        self.asm.append(".align 3")
        self.asm.append("pilha: .space 4096")
        self.asm.append("topo_pilha:")
        return self.asm


def gerarAssembly(todos_tokens, codigo) -> None:
    gerador = _Gerador()
    codigo.extend(gerador.montar(todos_tokens))

