"""
Tabela de Símbolos (Seção 2.7 do livro do Dragão).

É a estrutura onde o compilador anota informações sobre cada NOME que
aparece no programa (variáveis, funções, palavras reservadas...).

Quem usa:
  - O ANALISADOR LÉXICO cria a entrada quando vê o nome pela 1ª vez.
  - O ANALISADOR SEMÂNTICO preenche o campo 'tipo' (ao ver "int a;")
    e consulta a tabela para saber se uma variável foi declarada.
"""

from dataclasses import dataclass


@dataclass
class Simbolo:
    """Uma linha da tabela: tudo o que sabemos sobre um nome."""
    ordem: int            # posição de inserção (1, 2, 3...) - o barema pede isso
    lexema: str           # o nome em si: "a", "int", "main"
    categoria: str        # "identificador" ou "palavra reservada"
    tipo: str | None      # "int", "float"... Começa vazio (None) e é
                          # preenchido pela fase semântica
    linha: int            # linha da primeira vez que apareceu
    ocorrencias: int = 1  # quantas vezes o nome aparece no código


class TabelaSimbolos:
    def __init__(self):
        # Dicionário: chave = lexema, valor = Simbolo.
        # O dict do Python guarda a ORDEM em que os itens foram inseridos,
        # então a "ordem de inserção" do barema sai de graça.
        self._simbolos: dict[str, Simbolo] = {}

    def inserir(self, lexema: str, categoria: str, linha: int) -> Simbolo:
        """Insere o símbolo se for novo; se já existe, só conta mais uma ocorrência."""
        if lexema in self._simbolos:
            simbolo = self._simbolos[lexema]
            simbolo.ocorrencias += 1
            return simbolo

        # Símbolo novo: a ordem é o tamanho atual da tabela + 1
        simbolo = Simbolo(len(self._simbolos) + 1, lexema, categoria, None, linha)
        self._simbolos[lexema] = simbolo
        return simbolo

    def buscar(self, lexema: str) -> Simbolo | None:
        """Devolve o símbolo, ou None se ele não estiver na tabela."""
        return self._simbolos.get(lexema)

    def definir_tipo(self, lexema: str, tipo: str) -> None:
        """Registra o tipo de uma variável (usado pela fase semântica)."""
        self._simbolos[lexema].tipo = tipo

    def __iter__(self):
        """Permite escrever 'for s in tabela' e percorrer na ordem de inserção."""
        return iter(self._simbolos.values())

    def __len__(self):
        """Permite usar len(tabela)."""
        return len(self._simbolos)

    def exibir(self) -> str:
        """Monta o texto da tabela, bonito e alinhado, para imprimir no terminal."""
        linhas = [
            f"{'Ordem':<6}{'Lexema':<14}{'Categoria':<20}{'Tipo':<8}{'1ª linha':<9}{'Ocorr.'}",
            "-" * 64,
        ]
        for s in self:
            linhas.append(
                f"{s.ordem:<6}{s.lexema:<14}{s.categoria:<20}"
                f"{s.tipo or '-':<8}{s.linha:<9}{s.ocorrencias}"
            )
        return "\n".join(linhas)