"""
Analisador semântico (Seção 2.7 e Seção 6.5 do livro).

Percorre a AST e verifica o SENTIDO do código, usando a tabela de símbolos:
  1. Variável usada sem ter sido declarada
  2. Atribuição de tipos incompatíveis (String em int, por exemplo)
  3. Variável declarada mais de uma vez

Ao ler uma declaração, este módulo também PREENCHE a coluna 'Tipo' da
tabela de símbolos, que o léxico deixou vazia.
"""

from dataclasses import dataclass

from ..simbolos import TabelaSimbolos
from ..sintatico import No


@dataclass
class ErroSemantico:
    """Um problema de sentido encontrado no código."""
    mensagem: str
    linha: int

    def __str__(self):
        return f"[ERRO SEMÂNTICO] {self.mensagem}"


def _tipo_do_numero(texto: str) -> str:
    """'42' e '0xFF' são int; '2.5' e '1e3' são float."""
    t = texto.lower()
    if t.startswith("0x"):          # hexadecimal: checar ANTES do 'e'
        return "int"
    if "." in t or "e" in t:
        return "float"
    return "int"


class Analisador:
    def __init__(self, tabela: TabelaSimbolos):
        self.tabela = tabela
        self.erros: list[ErroSemantico] = []

    def analisar(self, ast: No) -> None:
        """Visita cada comando do programa, na ordem em que aparecem."""
        for comando in ast.filhos:
            if comando.rotulo == "Declaracao":
                self._declaracao(comando)
            elif comando.rotulo == "Atribuicao":
                self._atribuicao(comando)

    # ------------------------------------------------------------------
    # Comandos
    # ------------------------------------------------------------------
    def _declaracao(self, no: No) -> None:
        """Filhos: TIPO, ID e, se houver inicialização, OP_ATRIB e expressão."""
        tipo = no.filhos[0].valor
        nome = no.filhos[1]
        simbolo = self.tabela.buscar(nome.valor)

        if simbolo is not None and simbolo.tipo is not None:
            # O nome já tem tipo: foi declarado antes
            self.erros.append(ErroSemantico(
                f"Variável '{nome.valor}' declarada na linha {nome.linha} "
                f"já foi declarada anteriormente.",
                nome.linha,
            ))
        else:
            # Primeira declaração: anota o tipo na tabela de símbolos
            self.tabela.definir_tipo(nome.valor, tipo)

        # Declaração com valor inicial: "int a = <expressão>;"
        if len(no.filhos) == 4:
            tipo_alvo = self.tabela.buscar(nome.valor).tipo
            tipo_valor = self._tipo_da_expressao(no.filhos[3])
            self._checar_compatibilidade(tipo_alvo, tipo_valor, nome.linha)

    def _atribuicao(self, no: No) -> None:
        """Filhos: ID, OP_ATRIB e a expressão do lado direito."""
        alvo = no.filhos[0]
        simbolo = self.tabela.buscar(alvo.valor)
        tipo_alvo = simbolo.tipo if simbolo else None

        if tipo_alvo is None:
            self._erro_nao_declarada(alvo)

        tipo_valor = self._tipo_da_expressao(no.filhos[2])

        if tipo_alvo is not None:
            self._checar_compatibilidade(tipo_alvo, tipo_valor, alvo.linha)

    # ------------------------------------------------------------------
    # Tipos e verificações
    # ------------------------------------------------------------------
    def _tipo_da_expressao(self, no: No) -> str | None:
        """
        Descobre o tipo do valor que a expressão produz.
        Devolve None quando não dá para saber (houve variável não declarada).
        """
        if no.rotulo == "ID":
            simbolo = self.tabela.buscar(no.valor)
            if simbolo is None or simbolo.tipo is None:
                self._erro_nao_declarada(no)
                return None
            return simbolo.tipo

        if no.rotulo == "NUM":
            return _tipo_do_numero(no.valor)
        if no.rotulo == "CHAR":
            return "char"
        if no.rotulo == "STRING":
            return "String"

        if no.rotulo == "Expressao":
            # Visita os dois lados (mesmo que o primeiro dê erro, para
            # reportar todas as variáveis não declaradas)
            esquerda = self._tipo_da_expressao(no.filhos[0])
            direita = self._tipo_da_expressao(no.filhos[1])
            if esquerda is None or direita is None:
                return None
            if "String" in (esquerda, direita):
                return "String"
            # Regra do C: se um lado é float, o resultado é float
            return "float" if "float" in (esquerda, direita) else "int"

        return None

    def _checar_compatibilidade(self, tipo_alvo: str, tipo_valor: str | None,
                                linha: int) -> None:
        """Hoje só recusa String em variável numérica ou char."""
        if tipo_valor == "String":
            self.erros.append(ErroSemantico(
                f"Incompatibilidade de tipos na linha {linha}: "
                f"Não é possível atribuir String a um tipo {tipo_alvo}.",
                linha,
            ))

    def _erro_nao_declarada(self, no: No) -> None:
        self.erros.append(ErroSemantico(
            f"Variável '{no.valor}' utilizada na linha {no.linha} "
            f"não foi declarada previamente.",
            no.linha,
        ))


def analisar_semantico(ast: No, tabela: TabelaSimbolos) -> list[ErroSemantico]:
    """Executa a análise semântica. Devolve a lista de erros."""
    analisador = Analisador(tabela)
    analisador.analisar(ast)
    return analisador.erros