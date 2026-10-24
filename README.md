# Mini Compilador (front-end de C em Python)

Analisador escrito em **Python** que lê um arquivo de código-fonte **C** (`.c`) e executa três fases de análise:

1. **Análise léxica**: lista de tokens (tipo e lexema) e tabela de símbolos
2. **Análise sintática simplificada**: gramática livre de contexto (BNF) e impressão da AST
3. **Análise semântica simplificada**: variável não declarada, tipos incompatíveis e redeclaração

Trabalho da disciplina de Compiladores (P90100006), Unijorge, 2026.2.
Referência principal: AHO, A. V. et al. *Compiladores: princípios, técnicas e ferramentas*. 2. ed. Pearson, 2008.

> O programa **não executa** nem gera binário do código C. Ele apenas lê o arquivo como texto e analisa.

## Requisitos

- Python 3.10 ou superior
- `pytest` (apenas para rodar os testes)

## Instalação

```
git clone https://github.com/WendelMuniz/mini-compilador.git
cd mini-compilador
python -m venv .venv
.venv\Scripts\Activate.ps1        # Windows (PowerShell)
# source .venv/bin/activate       # Linux / macOS
pip install -r requirements.txt
```

## Como rodar

```
python main.py caminho/do/arquivo.c
```

Exemplos:

```
python main.py exemplos/sintatico_ok.c
python main.py C:\Users\fulano\Downloads\teste.c
```

Se o caminho tiver espaços, use aspas: `python main.py "C:\Minha Pasta\arquivo.c"`.

## O que o programa imprime

| Seção | Conteúdo |
|---|---|
| Análise léxica | Todos os tokens com linha:coluna, tipo e lexema |
| Tabela de símbolos | Ordem de inserção, lexema, categoria, tipo, 1ª linha e ocorrências |
| Erros léxicos | Caracteres inválidos, strings e comentários não fechados |
| Análise sintática | Uma AST para cada declaração ou atribuição reconhecida |
| Erros sintáticos | Mensagem com linha e coluna |
| Análise semântica | Erros de sentido encontrados (ou "Nenhum erro semântico") |

Exemplo de AST para `x = a + 5;`:

```
Atribuicao
├── ID (x)
├── OP_ATRIB (=)
└── Expressao (+)
    ├── ID (a)
    └── NUM (5)
```

## Gramática (BNF)

```
<Programa>    ::= <Comando>* EOF
<Comando>     ::= <Declaracao> | <Atribuicao>
<Declaracao>  ::= <tipo> ID [ "=" <Expressao> ] ";"
<Atribuicao>  ::= ID "=" <Expressao> ";"
<Expressao>   ::= <Termo> ( ("+" | "-") <Termo> )*
<Termo>       ::= <Fator> ( ("*" | "/" | "%") <Fator> )*
<Fator>       ::= ID | NUM | CHAR | STRING | "(" <Expressao> ")"
<tipo>        ::= "int" | "float" | "char"
```

## Verificações semânticas

| Situação | Mensagem |
|---|---|
| Variável usada sem declaração | `Variável 'total' utilizada na linha X não foi declarada previamente.` |
| String atribuída a tipo numérico | `Incompatibilidade de tipos na linha X: Não é possível atribuir String a um tipo int.` |
| Variável declarada duas vezes | `Variável 'a' declarada na linha X já foi declarada anteriormente.` |

## Testes

```
pytest -v
```

São 25 testes automáticos (léxico, sintático e semântico).

## Estrutura do projeto

```
mini-compilador/
├── main.py                        ponto de entrada
├── src/minicomp/
│   ├── lexico/                    tokens, regras (regex) e lexer
│   ├── simbolos/                  tabela de símbolos
│   ├── sintatico/                 parser descendente recursivo e AST
│   └── semantico/                 verificações semânticas
├── tests/                         testes automáticos (pytest)
├── exemplos/                      arquivos .c de demonstração
└── docs/gramatica.md              gramática em BNF
```

## Decisões de projeto e limitações

- **Léxico completo para C89**: 32 palavras reservadas, operadores, literais, comentários e diretivas. Erros léxicos usam *modo pânico*: o erro é registrado e a análise continua.
- **Diretivas** (`#include`, `#define`) viram um único token `DIRETIVA`, pois pertencem ao pré-processador.
- **Sintático restrito**: reconhece apenas declarações e atribuições simples. Outros trechos de C (funções, `if`, `while`, chamadas) são ignorados pela análise sintática.
- **Tabela de símbolos única**, sem escopos: variáveis de funções diferentes com o mesmo nome são tratadas como a mesma.
- **`float` em `int` é aceito**, como em C (o valor é truncado). Só `String` em variável numérica ou `char` gera erro de tipo.