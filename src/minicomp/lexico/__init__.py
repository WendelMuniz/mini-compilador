"""Pacote da análise léxica. Exporta o que as outras fases precisam."""

from .lexer import analisar_lexico
from .tokens import ErroLexico, Token

__all__ = ["analisar_lexico", "Token", "ErroLexico"]