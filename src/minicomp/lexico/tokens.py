"""
Estruturas de dados da análise léxica.

Conceitos (Seção 3.1 do livro):
  - TOKEN:   a categoria do pedaço de texto (ex.: NUM_INT, ID, PONTO_VIRGULA)
  - LEXEMA:  o texto concreto que casou (ex.: "42", "soma", ";")
  - PADRÃO:  a regra (expressão regular) que descreve o token
             (os padrões ficam em especificacao.py)
"""

from dataclasses import dataclass


@dataclass
class Token:
    """Um token reconhecido no código-fonte."""
    tipo: str     # categoria, ex.: "ID"
    lexema: str   # texto original, ex.: "soma"
    linha: int    # linha onde começa (a contagem começa em 1)
    coluna: int   # coluna onde começa (a contagem começa em 1)


@dataclass
class ErroLexico:
    """Um problema encontrado durante a análise léxica."""
    mensagem: str
    linha: int
    coluna: int

    def __str__(self):
        # Chamado automaticamente quando fazemos print(erro)
        return f"[ERRO LÉXICO] {self.mensagem} (linha {self.linha}, coluna {self.coluna})"