
from error import ExecutionError
from parser import RpnAtom


def aplicar_op(a: float, b: float, op: str) -> float:
    if op == "+":
        return a + b
    if op == "-":
        return a - b
    if op == "*":
        return a * b
    if op == "/":
        if b == 0:
            raise ExecutionError("Division by zero.")
        return a / b
    if op == "//":
        ia, ib = int(a), int(b)
        if ib == 0:
            raise ExecutionError("Integer division by zero.")
        return ia // ib
    if op == "%":
        ia, ib = int(a), int(b)
        if ib == 0:
            raise ExecutionError("Modulo by zero.")
        return ia % ib
    if op == "^":
        return a**b
    raise ExecutionError(f"Unknown operator: {op!r}.")


class ContextoExecucao:
    def __init__(self) -> None:
        self.memoria: dict[str, float] = {}
        self.historico: list[float] = []

    def executar_raiz(self, rpn: list[RpnAtom]) -> float:
        resultado = self.executar_rpn(rpn)
        self.historico.append(resultado)
        return resultado

    def executar_rpn(self, rpn: list[RpnAtom]) -> float:
        stack: list[float] = []

        for atom in rpn:
            tag = atom[0]

            if tag == "num":
                stack.append(float(atom[1]))

            elif tag == "var":
                stack.append(self.memoria.get(atom[1], 0.0))

            elif tag == "op":
                if len(stack) < 2:
                    raise ExecutionError("Not enough operands on stack for binary operator.")
                b = stack.pop()
                a = stack.pop()
                stack.append(aplicar_op(a, b, atom[1]))

            elif tag == "res":
                if len(stack) < 1:
                    raise ExecutionError("Not enough values on stack for RES.")
                n = int(stack.pop())
                if n < 0:
                    raise ExecutionError("RES index N must be non-negative.")
                if n >= len(self.historico):
                    raise ExecutionError("RES index N is out of range for history.")
                idx = len(self.historico) - 1 - n
                stack.append(self.historico[idx])

            elif tag == "store":
                if len(stack) < 1:
                    raise ExecutionError("Not enough values on stack for assignment.")
                valor = stack.pop()
                nome = atom[1]
                self.memoria[nome] = valor
                stack.append(valor)

            else:
                raise ExecutionError(f"Unknown RPN atom: {atom!r}.")

        if len(stack) != 1:
            raise ExecutionError(
                f"RPN evaluation must leave exactly one value on stack (got {len(stack)})."
            )
        return stack[0]
