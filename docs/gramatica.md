<Programa>    ::= <Comando>* EOF
<Comando>     ::= <Declaracao> | <Atribuicao>
<Declaracao>  ::= <tipo> ID [ "=" <Expressao> ] ";"
<Atribuicao>  ::= ID "=" <Expressao> ";"
<Expressao>   ::= <Termo> ( ("+" | "-") <Termo> )*
<Termo>       ::= <Fator> ( ("*" | "/" | "%") <Fator> )*
<Fator>       ::= ID | NUM | CHAR | STRING | "(" <Expressao> ")"
<tipo>        ::= "int" | "float" | "char"