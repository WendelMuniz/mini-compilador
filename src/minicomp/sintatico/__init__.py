"""Pacote da análise sintática. Exporta o que as outras fases precisam."""

from .arvore import No
from .parser import ErroSintatico, analisar_sintatico

__all__ = ["analisar_sintatico", "No", "ErroSintatico"]