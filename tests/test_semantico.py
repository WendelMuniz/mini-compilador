"""Testes automáticos da análise semântica."""

from minicomp.lexico import analisar_lexico
from minicomp.semantico import analisar_semantico
from minicomp.sintatico import analisar_sintatico


def analisar(codigo):
    """Auxiliar: roda as três fases e devolve (tabela, erros semânticos)."""
    tokens, tabela, _ = analisar_lexico(codigo)
    ast, _ = analisar_sintatico(tokens)
    erros = analisar_semantico(ast, tabela)
    return tabela, erros


def test_declaracao_preenche_tipo_na_tabela():
    tabela, erros = analisar("int a; float m;")
    assert erros == []
    assert tabela.buscar("a").tipo == "int"
    assert tabela.buscar("m").tipo == "float"


def test_variavel_nao_declarada_mensagem_do_barema():
    _, erros = analisar("total = 10;")
    assert len(erros) == 1
    assert erros[0].mensagem == (
        "Variável 'total' utilizada na linha 1 não foi declarada previamente."
    )


def test_variavel_nao_declarada_dentro_de_expressao():
    _, erros = analisar("int a;\na = b + 1;")
    assert len(erros) == 1
    assert "'b'" in erros[0].mensagem
    assert "linha 2" in erros[0].mensagem


def test_incompatibilidade_string_em_int_mensagem_do_barema():
    _, erros = analisar('int resultado = "texto";')
    assert len(erros) == 1
    assert erros[0].mensagem == (
        "Incompatibilidade de tipos na linha 1: "
        "Não é possível atribuir String a um tipo int."
    )


def test_redeclaracao():
    _, erros = analisar("int a;\nint a;")
    assert len(erros) == 1
    assert "já foi declarada" in erros[0].mensagem


def test_programa_correto_nao_gera_erros():
    _, erros = analisar("int a = 10; float m = 2.5; m = a * 2 + 1; char c = 'x';")
    assert erros == []


def test_float_em_int_e_permitido_como_no_c():
    _, erros = analisar("int x = 2.5;")
    assert erros == []