"""
Especificação léxica da linguagem C: as REGRAS do analisador.

Aqui definimos QUAIS tokens existem e COMO reconhecê-los, usando
expressões regulares (Seção 3.3 do livro). O algoritmo que aplica
estas regras está em lexer.py.
"""

import re

# As 32 palavras reservadas do C (padrão C89/C90).
# frozenset é um conjunto imutável; "x in conjunto" é uma busca muito rápida.
PALAVRAS_RESERVADAS = frozenset("""
    auto break case char const continue default do double else enum extern
    float for goto if int long register return short signed sizeof static
    struct switch typedef union unsigned void volatile while
""".split())

# Lista de pares (nome do token, expressão regular).
#
# REGRA DE OURO: a ORDEM IMPORTA. A regex tenta os padrões de cima para
# baixo e o primeiro que casar vence. Por isso:
#   - "<=" precisa vir antes de "<"   (senão "<=" viraria "<" e "=")
#   - NUM_FLOAT precisa vir antes de NUM_INT (senão "3.14" viraria "3", ".", "14")
#   - comentários vêm antes de OP_ARIT (senão "//" viraria dois "/")
ESPECIFICACAO = [
    # --- coisas que o parser nunca verá (serão descartadas) ---
    ("COMENTARIO_BLOCO",  r"/\*.*?\*/"),        # /* ... */  (o ? torna o .* "preguiçoso")
    ("COMENTARIO_ABERTO", r"/\*.*"),            # /* sem fechar -> será um ERRO
    ("COMENTARIO_LINHA",  r"//[^\n]*"),         # // até o fim da linha
    ("ESPACO",            r"\s+"),              # espaços, tabs, quebras de linha

    # --- diretivas do pré-processador ---
    ("DIRETIVA",          r"\#[^\n]*"),         # #include, #define... (linha inteira)

    # --- literais (valores escritos direto no código) ---
    ("STRING",            r'"(?:\\.|[^"\\\n])*"'),   # "texto" aceitando \n, \", etc.
    ("STRING_ABERTA",     r'"[^\n]*'),               # " sem fechar -> ERRO
    ("CHAR",              r"'(?:\\.|[^'\\\n])'"),    # 'a', '\n'
    ("CHAR_INVALIDO",     r"'"),                     # ' malformado -> ERRO
    ("NUM_FLOAT",         r"\d+\.\d*(?:[eE][+-]?\d+)?[fF]?"   # 3.14  3.  2.5e10
                          r"|\.\d+(?:[eE][+-]?\d+)?[fF]?"     # .5
                          r"|\d+[eE][+-]?\d+[fF]?"),          # 1e5
    ("NUM_INT",           r"0[xX][0-9a-fA-F]+|\d+"),          # 0xFF  ou  42

    # --- identificadores (as palavras reservadas são separadas depois, no lexer) ---
    ("ID",                r"[A-Za-z_][A-Za-z_0-9]*"),

    # --- operadores (os mais LONGOS primeiro) ---
    ("OP_ATRIB_COMPOSTO", r"<<=|>>=|[+\-*/%&|^]="),   # +=  -=  *=  <<=  ...
    ("OP_INCR_DECR",      r"\+\+|--"),                # ++  --
    ("OP_SETA",           r"->"),                     # ->
    ("OP_DESLOC",         r"<<|>>"),                  # <<  >>
    ("OP_REL",            r"==|!=|<=|>=|<|>"),        # comparações
    ("OP_LOGICO",         r"&&|\|\||!"),              # &&  ||  !
    ("OP_ATRIB",          r"="),                      # =
    ("OP_ARIT",           r"[+\-*/%]"),               # + - * / %
    ("OP_BIT",            r"[&|^~]"),                 # operadores bit a bit

    # --- delimitadores e pontuação ---
    ("ABRE_PAREN",        r"\("),
    ("FECHA_PAREN",       r"\)"),
    ("ABRE_CHAVE",        r"\{"),
    ("FECHA_CHAVE",       r"\}"),
    ("ABRE_COLCHETE",     r"\["),
    ("FECHA_COLCHETE",    r"\]"),
    ("PONTO_VIRGULA",     r";"),
    ("VIRGULA",           r","),
    ("PONTO",             r"\."),
    ("DOIS_PONTOS",       r":"),
    ("INTERROGACAO",      r"\?"),

    # --- rede de segurança: qualquer outro caractere é um ERRO ---
    ("ERRO",              r"."),
]

# Junta todos os padrões em UMA regex só.
# Cada padrão vira um "grupo nomeado" (?P<NOME>padrão); os grupos são
# separados por "|" (que significa "ou"). Depois, m.lastgroup nos diz
# qual grupo casou.
REGEX_MESTRA = re.compile(
    "|".join(f"(?P<{nome}>{padrao})" for nome, padrao in ESPECIFICACAO),
    re.DOTALL,   # faz o "." casar também com quebra de linha (necessário p/ /* ... */)
)

# Tokens que o lexer descarta (não vão para a lista de tokens)
IGNORADOS = {"ESPACO", "COMENTARIO_LINHA", "COMENTARIO_BLOCO"}

# Tokens que, na verdade, são erros, com a mensagem a mostrar para cada um
MENSAGENS_ERRO = {
    "COMENTARIO_ABERTO": "Comentário de bloco '/*' não foi fechado",
    "STRING_ABERTA": "String não foi fechada",
    "CHAR_INVALIDO": "Literal de caractere inválido",
    "ERRO": "Caractere inesperado",
}