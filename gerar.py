# Script pra gerar o Assembly e salvar os tokens
# Uso: python gerar.py <arquivo.txt>

import sys
import json
from lexer import Lexer
from assembly_generator import lerArquivo, gerarAssembly


def main():
    if len(sys.argv) < 2:
        print(f"Uso: python {sys.argv[0]} <arquivo.txt>")
        sys.exit(1)

    arquivo = sys.argv[1]

    linhas = []
    if not lerArquivo(arquivo, linhas):
        sys.exit(1)
    print(f"Arquivo '{arquivo}' lido. {len(linhas)} expressão(ões).\n")

    lexer = Lexer()
    todos_tokens = []
    for i, linha in enumerate(linhas):
        tokens = lexer.parseExpressao(linha)
        todos_tokens.append(tokens)

    # salva tokens em json
    dados = []
    for tks in todos_tokens:
        dados.append([{"type": t.token_type.name, "lexeme": t.lexeme} for t in tks])
    with open("tokens_output.txt", "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=2, ensure_ascii=False)
    print(f"\nTokens salvos em: tokens_output.txt")

    # gera assembly
    codigo = []
    gerarAssembly(todos_tokens, codigo)
    nome_asm = arquivo.rsplit(".", 1)[0] + ".s"
    with open(nome_asm, "w", encoding="utf-8") as f:
        f.write("\n".join(codigo))
    print(f"Assembly gerado em: {nome_asm}")


if __name__ == "__main__":
    main()
