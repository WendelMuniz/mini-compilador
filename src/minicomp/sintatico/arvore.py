"""
Nós da Árvore Sintática Abstrata (AST).

A AST é a árvore que o parser constrói para mostrar a ESTRUTURA do código.
Cada nó tem um rótulo (ex.: "Atribuicao"), um valor opcional (ex.: "x")
e uma lista de filhos.

Este arquivo só DESCREVE a árvore e sabe se desenhar no terminal.
Quem constrói a árvore é o parser (parser.py).
"""

from dataclasses import dataclass, field


@dataclass
class No:
    """Um nó da árvore."""
    rotulo: str                    # tipo do nó, ex.: "Atribuicao", "ID", "NUM"
    valor: str | None = None       # texto do token, ex.: "x" (None em nós internos)
    filhos: list["No"] = field(default_factory=list)   # nós abaixo deste
    linha: int = 0                 # linha do código (útil para mensagens de erro)

    def __str__(self) -> str:
        """Como o nó aparece escrito: 'ID (x)' ou só 'Atribuicao'."""
        if self.valor is not None:
            return f"{self.rotulo} ({self.valor})"
        return self.rotulo

    def exibir(self) -> str:
        """Desenha a árvore inteira, a partir deste nó, com ├── e └──."""
        linhas = [str(self)]
        self._desenhar_filhos("", linhas)
        return "\n".join(linhas)

    def _desenhar_filhos(self, prefixo: str, linhas: list[str]) -> None:
        """
        Percorre os filhos e acrescenta uma linha para cada um.

        'prefixo' é o recuo acumulado dos níveis acima: "│   " se o pai ainda
        tem irmãos depois dele (a linha vertical continua), ou "    " se o pai
        era o último (não há mais nada para ligar).
        """
        for i, filho in enumerate(self.filhos):
            eh_ultimo = (i == len(self.filhos) - 1)
            conector = "└── " if eh_ultimo else "├── "
            linhas.append(prefixo + conector + str(filho))
            # Chamada recursiva: o filho desenha os filhos dele
            filho._desenhar_filhos(prefixo + ("    " if eh_ultimo else "│   "), linhas)