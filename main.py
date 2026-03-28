# - Felipe Augusto Baleche Goncalves - FelipeABG
# - Giuseppe Bruno Ferreira Filippin - giuseppefilippin
# - Isabelle Lopes Kulczynskyj - isaabellelopes
# - Pedro Bastos Leite - PedroLeite3005

# Grupo: RA1 10

import sys

from error import (
    ExecutionError,
    InvalidNumberException,
    InvalidTokenException,
    LowerCaseException,
    ParseError,
)
from assembly_generator import salvar_assembly, lerArquivo
from executor import ContextoExecucao
from lexer import Lexer
from parser import parse


def exibir_resultados(resultados: list[float]) -> None:
    for x in resultados:
        print(f"{x:.1f}")


def processar_linhas(linhas: list[str]) -> list[float]:
    ctx = ContextoExecucao()
    lexer = Lexer()
    resultados: list[float] = []
    for raw in linhas:
        line = raw.strip()
        if not line:
            continue
        tokens = lexer.parseExpressao(line)
        rpn = parse(tokens)
        resultados.append(ctx.executarExpressao(rpn))
    return resultados

def main() -> None:
    try:
        file_path = sys.argv[1]
    except IndexError:
        print(f"Usage: {sys.argv[0]} [path-to-file]", file=sys.stderr)
        sys.exit(1)

    linhas: list[str] = []
    if not lerArquivo(file_path, linhas):
        sys.exit(1)

    try:
        resultados = processar_linhas(linhas)
    except (
        LowerCaseException,
        InvalidNumberException,
        InvalidTokenException,
        ParseError,
        ExecutionError,
    ) as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)

    exibir_resultados(resultados)
    salvar_assembly(file_path, linhas)


if __name__ == "__main__":
    main()
