"""
Analisador sintático (Cap. 4 do livro).

Técnica: ANÁLISE DESCENDENTE RECURSIVA (Seção 4.4). Cada não-terminal da
gramática (veja docs/gramatica.md) vira uma função. As funções chamam
umas às outras e, ao fazer isso, reproduzem as regras da gramática e
constroem a AST.

Escopo: só declarações e atribuições. O resto do C é ignorado.
Erros: "modo pânico" - registra o erro, pula até o próximo ';' e continua.
"""

from ..lexico import Token
from .arvore import No

# Palavras reservadas que iniciam uma declaração
TIPOS = {"int", "float", "char"}

# Tokens que, vindos logo depois de "tipo ID", indicam que NÃO é uma
# declaração simples (é função, parâmetro ou vetor): o parser ignora.
IGNORAR_APOS_ID = {"ABRE_PAREN", "VIRGULA", "FECHA_PAREN", "ABRE_COLCHETE"}

# Tokens que são valores escritos direto no código, e o rótulo que
# eles recebem na árvore.
LITERAIS = {
    "NUM_INT": "NUM",
    "NUM_FLOAT": "NUM",
    "CHAR": "CHAR",
    "STRING": "STRING",
}


class ErroSintatico(Exception):
    """Erro de sintaxe. Herda de Exception para podermos usar raise/except."""

    def __init__(self, mensagem: str, linha: int, coluna: int):
        super().__init__(mensagem)
        self.mensagem = mensagem
        self.linha = linha
        self.coluna = coluna

    def __str__(self):
        return f"[ERRO SINTÁTICO] {self.mensagem} (linha {self.linha}, coluna {self.coluna})"


class Parser:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.pos = 0                       # índice do token atual
        self.erros: list[ErroSintatico] = []

    # ------------------------------------------------------------------
    # Funções auxiliares: andar pela lista de tokens
    # ------------------------------------------------------------------
    def _atual(self) -> Token:
        """Token que estamos olhando agora (sem consumir)."""
        return self.tokens[self.pos]

    def _olhar(self, distancia: int) -> Token:
        """Espia um token à frente. Nunca passa do EOF, que é o último."""
        return self.tokens[min(self.pos + distancia, len(self.tokens) - 1)]

    def _avancar(self) -> Token:
        """Consome o token atual e o devolve. O EOF nunca é consumido."""
        token = self._atual()
        if token.tipo != "EOF":
            self.pos += 1
        return token

    def _erro(self, esperado: str) -> ErroSintatico:
        """Monta um erro do tipo 'Esperado X, encontrado Y'."""
        token = self._atual()
        encontrado = "fim do arquivo" if token.tipo == "EOF" else repr(token.lexema)
        return ErroSintatico(
            f"Esperado {esperado}, encontrado {encontrado}", token.linha, token.coluna
        )

    def _consumir(self, tipo: str, descricao: str) -> Token:
        """Exige que o token atual seja do tipo dado; senão, lança erro."""
        if self._atual().tipo == tipo:
            return self._avancar()
        raise self._erro(descricao)

    # ------------------------------------------------------------------
    # Recuperação de erros (modo pânico)
    # ------------------------------------------------------------------
    def _sincronizar(self) -> None:
        """Descarta tokens até passar de um ';' (ou chegar a '}' / EOF)."""
        while self._atual().tipo != "EOF":
            token = self._avancar()
            if token.tipo == "PONTO_VIRGULA":
                return
            if self._atual().tipo == "FECHA_CHAVE":
                return

    # ------------------------------------------------------------------
    # Regras da gramática (uma função por não-terminal)
    # ------------------------------------------------------------------
    def programa(self) -> No:
        """<Programa> ::= <Comando>* EOF"""
        raiz = No("Programa")
        while self._atual().tipo != "EOF":
            try:
                comando = self._comando()
            except ErroSintatico as erro:
                self.erros.append(erro)      # anota o erro...
                self._sincronizar()          # ...e pula até o próximo ';'
                continue
            if comando is not None:
                raiz.filhos.append(comando)
        return raiz

    def _comando(self) -> No | None:
        """
        <Comando> ::= <Declaracao> | <Atribuicao>

        Decide pelo que vem pela frente (olhando 1 ou 2 tokens). Se não for
        nenhum dos dois, o token é ignorado: está fora da gramática.
        """
        token = self._atual()
        proximo = self._olhar(1)

        # "tipo ID ..." sem ser função/parâmetro/vetor -> declaração
        if (token.tipo == "PALAVRA_RESERVADA" and token.lexema in TIPOS
                and proximo.tipo == "ID"
                and self._olhar(2).tipo not in IGNORAR_APOS_ID):
            return self._declaracao()

        # "ID =" -> atribuição
        if token.tipo == "ID" and proximo.tipo == "OP_ATRIB":
            return self._atribuicao()

        self._avancar()   # fora da gramática: ignora este token
        return None

    def _declaracao(self) -> No:
        """<Declaracao> ::= <tipo> ID [ "=" <Expressao> ] ";" """
        tipo = self._avancar()
        nome = self._consumir("ID", "identificador")
        no = No("Declaracao", linha=tipo.linha, filhos=[
            No("TIPO", tipo.lexema, linha=tipo.linha),
            No("ID", nome.lexema, linha=nome.linha),
        ])
        if self._atual().tipo == "OP_ATRIB":          # parte opcional [ ... ]
            igual = self._avancar()
            no.filhos.append(No("OP_ATRIB", igual.lexema, linha=igual.linha))
            no.filhos.append(self._expressao())
        self._consumir("PONTO_VIRGULA", "';'")
        return no

    def _atribuicao(self) -> No:
        """<Atribuicao> ::= ID "=" <Expressao> ";" """
        nome = self._avancar()
        igual = self._consumir("OP_ATRIB", "'='")
        expressao = self._expressao()
        self._consumir("PONTO_VIRGULA", "';'")
        return No("Atribuicao", linha=nome.linha, filhos=[
            No("ID", nome.lexema, linha=nome.linha),
            No("OP_ATRIB", igual.lexema, linha=igual.linha),
            expressao,
        ])

    def _expressao(self) -> No:
        """<Expressao> ::= <Termo> ( ("+" | "-") <Termo> )*"""
        esquerda = self._termo()
        # O "*" da gramática virou um while. Cada volta junta o que já temos
        # (esquerda) com o próximo termo, formando um nó "Expressao (+)".
        while self._atual().tipo == "OP_ARIT" and self._atual().lexema in ("+", "-"):
            operador = self._avancar()
            direita = self._termo()
            esquerda = No("Expressao", operador.lexema, [esquerda, direita], operador.linha)
        return esquerda

    def _termo(self) -> No:
        """<Termo> ::= <Fator> ( ("*" | "/" | "%") <Fator> )*"""
        esquerda = self._fator()
        while self._atual().tipo == "OP_ARIT" and self._atual().lexema in ("*", "/", "%"):
            operador = self._avancar()
            direita = self._fator()
            esquerda = No("Expressao", operador.lexema, [esquerda, direita], operador.linha)
        return esquerda

    def _fator(self) -> No:
        """<Fator> ::= ID | NUM | CHAR | STRING | "(" <Expressao> ")" """
        token = self._atual()

        if token.tipo == "ID":
            self._avancar()
            return No("ID", token.lexema, linha=token.linha)

        if token.tipo in LITERAIS:
            self._avancar()
            return No(LITERAIS[token.tipo], token.lexema, linha=token.linha)

        if token.tipo == "ABRE_PAREN":
            self._avancar()
            interno = self._expressao()
            self._consumir("FECHA_PAREN", "')'")
            return interno   # os parênteses somem da AST: é isso que a torna "abstrata"

        raise self._erro("identificador, número ou '('")


def analisar_sintatico(tokens: list[Token]) -> tuple[No, list[ErroSintatico]]:
    """Executa a análise sintática. Devolve (ast, erros)."""
    parser = Parser(tokens)
    ast = parser.programa()
    return ast, parser.erros