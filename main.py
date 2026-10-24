"""
Ponto de entrada do compilador.

Uso:  python main.py arquivo.c

Lê o arquivo C e executa as três fases de análise:
léxica, sintática e semântica, imprimindo os resultados.
"""

import sys

# main.py fica FORA da pasta src/, então avisamos ao Python onde achar o
# pacote 'minicomp'. Esta linha precisa vir ANTES dos imports abaixo.
sys.path.insert(0, "src")

from minicomp.lexico import analisar_lexico
from minicomp.semantico import analisar_semantico
from minicomp.sintatico import analisar_sintatico


def titulo(texto: str) -> None:
    """Imprime um cabeçalho com linhas de '=' para separar as seções."""
    print("=" * 64)
    print(texto)
    print("=" * 64)


def main():
    # Garante que os caracteres da árvore (├── └──) saiam corretos
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

    # Confere se o usuário passou o nome do arquivo
    if len(sys.argv) != 2:
        print("Uso: python main.py arquivo.c")
        sys.exit(1)

    # Lê o arquivo. errors="replace" troca caracteres inválidos por '?',
    # em vez de travar o programa (importante: travar = nota zero).
    try:
        with open(sys.argv[1], encoding="utf-8", errors="replace") as f:
            codigo = f.read()
    except OSError as e:
        print(f"Não foi possível abrir o arquivo: {e}")
        sys.exit(1)

    # ---- Executa as três fases (ainda sem imprimir nada) ----
    tokens, tabela, erros_lex = analisar_lexico(codigo)
    ast, erros_sint = analisar_sintatico(tokens)
    erros_sem = analisar_semantico(ast, tabela)   # também preenche os tipos

    # ---- FASE 1: léxica ----
    titulo("ANÁLISE LÉXICA - LISTA DE TOKENS")
    print(f"{'Linha:Col':<10}{'Tipo':<20}Lexema")
    print("-" * 64)
    for t in tokens:
        print(f"{t.linha}:{t.coluna:<8}{t.tipo:<20}{t.lexema}")

    print()
    titulo("TABELA DE SÍMBOLOS")
    print(tabela.exibir())

    if erros_lex:
        print()
        titulo("ERROS LÉXICOS")
        for e in erros_lex:
            print(e)

    # ---- FASE 2: sintática ----
    print()
    titulo("ANÁLISE SINTÁTICA - AST")
    if ast.filhos:
        for comando in ast.filhos:
            print(comando.exibir())
            print()
    else:
        print("(nenhum comando reconhecido)")

    if erros_sint:
        titulo("ERROS SINTÁTICOS")
        for e in erros_sint:
            print(e)

    # ---- FASE 3: semântica ----
    print()
    titulo("ANÁLISE SEMÂNTICA")
    if erros_sem:
        for e in erros_sem:
            print(e)
    else:
        print("Nenhum erro semântico encontrado.")


if __name__ == "__main__":
    main()