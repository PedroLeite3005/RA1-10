# Compilador RPN → Assembly ARMv7 (Fase 1)

## Informações

**Universidade:** PUCPR - Pontifícia Universidade Católica do Paraná  
**Disciplina:** Construção de Interpretadores (Turma 7º A) - Ciência da Computação (Noite) - 2026  
**Professor:** Frank Coelho de Alcantara  
**Grupo:** RA1 10

### Alunos

- Felipe Augusto Baleche Goncalves - [@FelipeABG](https://github.com/FelipeABG)
- Giuseppe Bruno Ferreira Filippin - [@giuseppefilippin](https://github.com/giuseppefilippin)
- Isabelle Lopes Kulczynskyj - [@isaabellelopes](https://github.com/isaabellelopes)
- Pedro Bastos Leite - [@PedroLeite3005](https://github.com/PedroLeite3005)

---

## Sobre o Projeto

Programa em Python que lê expressões aritméticas em Notação Polonesa Reversa (RPN) de um arquivo de texto, realiza a análise léxica com Autômatos Finitos Determinísticos e gera código Assembly ARMv7 funcional para o simulador CPUlator DE1-SoC (v16.1).

### O que o programa faz

1. Lê um arquivo `.txt` com expressões RPN (uma por linha)
2. Analisa cada linha com o analisador léxico (AFD com funções de estado)
3. Gera código Assembly ARMv7 que executa todas as operações no CPUlator
4. Salva os tokens em `tokens_output.txt` e o Assembly em um arquivo `.s`

### Operações suportadas

- Adição: `(A B +)`
- Subtração: `(A B -)`
- Multiplicação: `(A B *)`
- Divisão real: `(A B /)`
- Divisão inteira: `(A B //)`
- Resto: `(A B %)`
- Potenciação: `(A B ^)` (B inteiro positivo)
- Armazenar variável: `(V MEM)`
- Ler variável: `(MEM)`
- Resultado anterior: `(N RES)`
- Expressões aninhadas sem limite: `((A B +) (C D *) /)`

---

## Estrutura dos Arquivos

```
├── main.py                 # Programa principal (integração)
├── tokens.py               # Tipos de tokens (TokenType, Token)
├── lexer.py                # Analisador léxico com AFD (parseExpressao)
├── parser.py               # Parser de expressões RPN
├── executor.py             # Executor de expressões (executarExpressao)
├── assembly_generator.py   # Gerador de Assembly ARMv7 (gerarAssembly + lerArquivo)
├── error.py                # Exceções personalizadas
├── gerar.py                # Script para gerar o Assembly e os tokens
├── test_lexer.py           # Testes do analisador léxico
├── test_executor.py        # Testes do executor
├── test_assembly.py        # Testes do gerador de Assembly e leitura de arquivo
├── teste1.txt              # Arquivo de teste 1 (12 expressões)
├── teste2.txt              # Arquivo de teste 2 (12 expressões)
├── teste3.txt              # Arquivo de teste 3 (12 expressões)
├── teste3.s                # Assembly ARMv7 gerado (última execução)
├── tokens_output.txt       # Tokens da última execução (formato JSON)
└── README.md               # Este arquivo
```

---

## Como Executar

### Pré-requisitos

- Python 3.10 ou superior

### Gerar o Assembly e os tokens

```bash
python3 main.py teste1.txt
```

Isso produz:

- `teste1.s` — código Assembly ARMv7
- `tokens_output.txt` — tokens em formato JSON

Funciona com qualquer um dos 3 arquivos de teste:

```bash
python3 main.py teste1.txt
python3 main.py teste2.txt
python3 main.py teste3.txt
```

### Executar o Assembly no CPUlator

1. Acesse [cpulator.01xz.net/?sys=arm-de1soc](https://cpulator.01xz.net/?sys=arm-de1soc)
2. Selecione **Language: ARMv7**
3. Copie e cole o conteúdo do arquivo `.s` gerado
4. Clique em **Compile and Load (F5)**
5. Clique em **Continue (F3)** para executar
6. Os resultados aparecem nos **LEDs** e no **display de 7 segmentos**

---

## Como Rodar os Testes

### Testes individuais

```bash
python3 -m unittest test_lexer -v        # Analisador léxico
python3 -m unittest test_executor -v     # Executor de expressões
python3 -m unittest test_assembly -v     # Gerador de Assembly e leitura de arquivo
```

---

## Divisão de Tarefas

| Aluno              | Função                                             | Arquivos                                                                |
| ------------------ | -------------------------------------------------- | ----------------------------------------------------------------------- |
| Pedro  (Aluno 1)   | `parseExpressao` + Analisador Léxico (AFD)         | `lexer.py`, `tokens.py`, `test_lexer.py`                                |
| Felipe   (Aluno 2) | `executarExpressao` + Memória + Histórico          | `executor.py`, `parser.py`, `test_executor.py`                          |
| Giuseppe (Aluno 3) | `gerarAssembly` + `lerArquivo` + Arquivos de teste | `assembly_generator.py`, `gerar.py`, `test_assembly.py`, `teste1-3.txt` |
| Isabelle (Aluno 4) | `exibirResultados` + `main` + Integração           | `main.py`, `error.py`                                                   |

---

## Detalhes Técnicos

### Analisador Léxico

Implementado com Autômatos Finitos Determinísticos, onde cada estado é uma função:

- `state_number()` — números inteiros e reais (ponto como separador)
- `state_operator()` — operadores `+`, `-`, `*`, `/`, `//`, `%`, `^`
- `state_identifier()` — variáveis em letras maiúsculas
- `state_keyword()` — keyword `RES`
- `state_parenthesis()` — parênteses `(` e `)`
- `state_space()` — espaços em branco

### Geração de Assembly

O código Assembly gerado usa IEEE 754 de 64 bits (double precision). Como o CPUlator DE1-SoC não possui FPU, todas as operações com double são implementadas em software (soft-float):

- `__aeabi_dadd` — soma de doubles
- `__aeabi_dsub` — subtração de doubles
- `__aeabi_dmul` — multiplicação de doubles
- `__aeabi_ddiv` — divisão de doubles
- `__aeabi_d2iz` — conversão double → inteiro
- `__aeabi_i2d` — conversão inteiro → double

Os resultados são exibidos nos periféricos do DE1-SoC:

- **LEDs** (endereço `0xFF200000`) — parte inteira do resultado em binário
- **Display HEX** (endereço `0xFF200020`) — parte inteira em hexadecimal no 7-segmentos

### Arquivos de Teste

Cada arquivo contém 12 expressões cobrindo todas as operações, comandos especiais e expressões aninhadas:

- **teste1.txt** — operações básicas, RES, MEM (RESULTADO), aninhamento
- **teste2.txt** — variáveis (VAR, PI), potência, aninhamento profundo
- **teste3.txt** — aninhamento triplo, múltiplas variáveis (TOTAL, PRODUTO), todas as operações
