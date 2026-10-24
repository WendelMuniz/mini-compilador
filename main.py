"""
Ponto de entrada do compilador.

Uso:  python main.py arquivo.c

Lê o arquivo C e executa as fases de análise, imprimindo os resultados.
"""

import sys

# main.py fica FORA da pasta src/, então avisamos ao Python onde achar o
# pacote 'minicomp'. Esta linha precisa vir ANTES do import abaixo.
sys.path.insert(0, "src")

from minicomp.lexico import analisar_lexico


def titulo(texto: str) -> None:
    """Imprime um cabeçalho com linhas de '=' para separar as seções."""
    print("=" * 64)
    print(texto)
    print("=" * 64)


def main():
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

    # ---- FASE 1: análise léxica ----
    tokens, tabela, erros = analisar_lexico(codigo)

    titulo("ANÁLISE LÉXICA - LISTA DE TOKENS")
    print(f"{'Linha:Col':<10}{'Tipo':<20}Lexema")
    print("-" * 64)
    for t in tokens:
        print(f"{t.linha}:{t.coluna:<8}{t.tipo:<20}{t.lexema}")

    print()
    titulo("TABELA DE SÍMBOLOS")
    print(tabela.exibir())

    if erros:
        print()
        titulo("ERROS LÉXICOS")
        for e in erros:
            print(e)


if __name__ == "__main__":
    main()
    