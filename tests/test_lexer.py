"""
Testes automáticos da análise léxica.

Cada função que começa com 'test_' é um teste. O pytest roda todas e
mostra quais passaram. 'assert X == Y' falha o teste se X for diferente de Y.
"""

from minicomp.lexico import analisar_lexico


def tipos(codigo):
    """Auxiliar: devolve só os tipos dos tokens (sem o EOF), exigindo zero erros."""
    tokens, _, erros = analisar_lexico(codigo)
    assert erros == []
    return [t.tipo for t in tokens][:-1]


def test_atribuicao_simples():
    assert tipos("x = a + 5;") == [
        "ID", "OP_ATRIB", "ID", "OP_ARIT", "NUM_INT", "PONTO_VIRGULA"
    ]


def test_palavra_reservada_vs_identificador():
    # "whilex" NÃO é palavra reservada, só começa igual a uma
    assert tipos("int whilex") == ["PALAVRA_RESERVADA", "ID"]


def test_numeros():
    assert tipos("42") == ["NUM_INT"]
    assert tipos("3.14") == ["NUM_FLOAT"]
    assert tipos("0xFF") == ["NUM_INT"]


def test_operadores_longos_antes_dos_curtos():
    assert tipos("a <= b") == ["ID", "OP_REL", "ID"]
    assert tipos("x += 1") == ["ID", "OP_ATRIB_COMPOSTO", "NUM_INT"]
    assert tipos("i++") == ["ID", "OP_INCR_DECR"]


def test_string_com_escape():
    assert tipos('printf("oi %d\\n", x);') == [
        "ID", "ABRE_PAREN", "STRING", "VIRGULA", "ID",
        "FECHA_PAREN", "PONTO_VIRGULA",
    ]


def test_comentarios_ignorados():
    assert tipos("x // linha\n /* bloco */ y") == ["ID", "ID"]


def test_diretiva():
    assert tipos("#include <stdio.h>") == ["DIRETIVA"]


def test_posicao_linha_coluna():
    tokens, _, _ = analisar_lexico("a\n  b")
    assert (tokens[1].linha, tokens[1].coluna) == (2, 3)


def test_erro_caractere_invalido_nao_para_a_analise():
    tokens, _, erros = analisar_lexico("x = @;")
    assert len(erros) == 1
    assert "@" in erros[0].mensagem
    assert (erros[0].linha, erros[0].coluna) == (1, 5)
    assert tokens[-2].tipo == "PONTO_VIRGULA"   # continuou depois do erro


def test_erro_string_e_comentario_abertos():
    _, _, erros = analisar_lexico('char *s = "abc;\n')
    assert len(erros) == 1
    _, _, erros = analisar_lexico("int x; /* sem fechar")
    assert len(erros) == 1


def test_tabela_de_simbolos_ordem_e_ocorrencias():
    _, tabela, _ = analisar_lexico("int a; int b; a = b;")
    assert [s.lexema for s in tabela] == ["int", "a", "b"]
    assert tabela.buscar("a").ocorrencias == 2
    assert tabela.buscar("int").categoria == "palavra reservada" 