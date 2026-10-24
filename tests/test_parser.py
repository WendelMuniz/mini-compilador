"""Testes automáticos da análise sintática."""

from minicomp.lexico import analisar_lexico
from minicomp.sintatico import analisar_sintatico


def ast_de(codigo):
    """Auxiliar: roda léxico + sintático e devolve (ast, erros)."""
    tokens, _, _ = analisar_lexico(codigo)
    return analisar_sintatico(tokens)


def test_atribuicao_igual_ao_barema():
    ast, erros = ast_de("x = a + 5;")
    assert erros == []
    assert ast.filhos[0].exibir() == (
        "Atribuicao\n"
        "├── ID (x)\n"
        "├── OP_ATRIB (=)\n"
        "└── Expressao (+)\n"
        "    ├── ID (a)\n"
        "    └── NUM (5)"
    )


def test_precedencia_multiplicacao_antes_da_soma():
    ast, _ = ast_de("x = a + b * 2;")
    expressao = ast.filhos[0].filhos[2]
    assert expressao.valor == "+"
    assert expressao.filhos[1].valor == "*"   # o * ficou mais fundo


def test_parenteses_mudam_a_estrutura():
    ast, _ = ast_de("x = (a + b) * 2;")
    expressao = ast.filhos[0].filhos[2]
    assert expressao.valor == "*"
    assert expressao.filhos[0].valor == "+"   # o + agora fica mais fundo


def test_declaracoes():
    ast, erros = ast_de("int a = 10; int b;")
    assert erros == []
    assert len(ast.filhos) == 2
    assert len(ast.filhos[0].filhos) == 4   # tipo, ID, =, valor
    assert len(ast.filhos[1].filhos) == 2   # tipo, ID


def test_erro_falta_ponto_virgula():
    _, erros = ast_de("int a = 1;\nb = a + 5\na = 3;")
    assert len(erros) == 1
    assert erros[0].linha == 3
    assert "';'" in erros[0].mensagem


def test_modo_panico_continua_depois_do_erro():
    ast, erros = ast_de("x = ; y = 2;")
    assert len(erros) == 1
    assert len(ast.filhos) == 1             # o "y = 2;" foi reconhecido


def test_codigo_fora_da_gramatica_e_ignorado():
    ast, erros = ast_de('int main() { printf("oi"); }')
    assert erros == []
    assert ast.filhos == []