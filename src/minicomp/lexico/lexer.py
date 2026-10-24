"""
Analisador léxico (Cap. 3 do livro).

Lê o código-fonte como uma sequência de caracteres e o agrupa em TOKENS,
construindo ao mesmo tempo a TABELA DE SÍMBOLOS.

Estratégia de erros: "modo pânico" (Seção 3.1.4). Ao achar algo inválido,
registramos o erro, descartamos o trecho e CONTINUAMOS, para reportar
todos os erros de uma vez, e não só o primeiro.
"""

from ..simbolos import TabelaSimbolos
from .especificacao import (
    IGNORADOS,
    MENSAGENS_ERRO,
    PALAVRAS_RESERVADAS,
    REGEX_MESTRA,
)
from .tokens import ErroLexico, Token


def _posicao(codigo: str, indice: int) -> tuple[int, int]:
    """
    Converte uma posição absoluta no texto em (linha, coluna), contando de 1.

    linha  = (quantidade de '\\n' antes da posição) + 1
    coluna = distância até o último '\\n' antes da posição
    """
    linha = codigo.count("\n", 0, indice) + 1
    coluna = indice - codigo.rfind("\n", 0, indice)
    return linha, coluna


def analisar_lexico(codigo: str):
    """
    Executa a análise léxica completa.

    Devolve uma tupla (tokens, tabela_de_simbolos, erros).
    """
    tokens: list[Token] = []
    erros: list[ErroLexico] = []
    tabela = TabelaSimbolos()

    # finditer percorre o texto da esquerda para a direita, devolvendo um
    # "match" para cada trecho que a REGEX_MESTRA reconhece.
    for m in REGEX_MESTRA.finditer(codigo):
        tipo = m.lastgroup   # nome do padrão que venceu (ex.: "NUM_INT")
        lexema = m.group()   # texto que casou (ex.: "42")

        # 1) Espaços e comentários: descartar
        if tipo in IGNORADOS:
            continue

        linha, coluna = _posicao(codigo, m.start())

        # 2) Erros: registrar e seguir em frente (modo pânico)
        if tipo in MENSAGENS_ERRO:
            mensagem = MENSAGENS_ERRO[tipo]
            if tipo == "ERRO":
                mensagem += f" {lexema!r}"   # mostra qual caractere foi
            erros.append(ErroLexico(mensagem, linha, coluna))
            continue

        # 3) Identificadores: podem ser palavras reservadas (Seção 3.1.2)
        #    e entram na tabela de símbolos.
        if tipo == "ID":
            if lexema in PALAVRAS_RESERVADAS:
                tipo = "PALAVRA_RESERVADA"
                tabela.inserir(lexema, "palavra reservada", linha)
            else:
                tabela.inserir(lexema, "identificador", linha)

        # 4) Token válido: guardar na lista
        tokens.append(Token(tipo, lexema, linha, coluna))

    # Token especial que marca o fim da entrada (o parser vai precisar dele)
    linha_fim, _ = _posicao(codigo, len(codigo))
    tokens.append(Token("EOF", "", linha_fim, 1))

    return tokens, tabela, erros