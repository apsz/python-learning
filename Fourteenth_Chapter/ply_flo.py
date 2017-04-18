#!/usr/bin/python3


import sys
import ply.lex
import ply.yacc


def get_file_handle(filename):
    try:
        return open(filename)
    except (EnvironmentError, IOError) as file_err:
        print('Error opening {}: {}'.format(filename, file_err))
        sys.exit()


def ply_parse(text):
    """
    >>> formula = "a = b"
    >>> print(ply_parse(formula))
    ['a', '=', 'b']
    >>> formula = "forall x: a = b"
    >>> print(ply_parse(formula))
    ['forall', 'x', ['a', '=', 'b']]
    >>> formula = "a & b"
    >>> print(ply_parse(formula))
    ['a', '&', 'b']
    >>> formula = "~true -> ~b = c"
    >>> print(ply_parse(formula))
    [['~', 'true'], '->', ['~', ['b', '=', 'c']]]
    >>> formula = "~true -> ~(b = c)"
    >>> print(ply_parse(formula))
    [['~', 'true'], '->', ['~', ['b', '=', 'c']]]
    >>> formula = "exists y: a -> b"
    >>> print(ply_parse(formula))
    ['exists', 'y', ['a', '->', 'b']]
    >>> formula = "forall x: exists y: a = b"
    >>> print(ply_parse(formula))
    ['forall', 'x', ['exists', 'y', ['a', '=', 'b']]]
    >>> formula = "forall x: exists y: a = b -> a = b & ~ a = b -> a = b"
    >>> print(ply_parse(formula))
    ['forall', 'x', ['exists', 'y', [['a', '=', 'b'], '->', [[['a', '=', 'b'], '&', ['~', ['a', '=', 'b']]], '->', ['a', '=', 'b']]]]]
    >>> formula = "(forall x: exists y: a = b) -> a = b & ~ a = b -> a = b"
    >>> print(ply_parse(formula))
    [['forall', 'x', ['exists', 'y', ['a', '=', 'b']]], '->', [[['a', '=', 'b'], '&', ['~', ['a', '=', 'b']]], '->', ['a', '=', 'b']]]
    >>> formula = "(forall x: exists y: true) -> true & ~ true -> true"
    >>> print(ply_parse(formula))
    [['forall', 'x', ['exists', 'y', 'true']], '->', [['true', '&', ['~', 'true']], '->', 'true']]
    >>> formula = "a = b -> c = d & e = f"
    >>> result1 = ply_parse(formula)
    >>> formula = "(a = b) -> (c = d & e = f)"
    >>> result2 = ply_parse(formula)
    >>> result1 == result2
    True
    >>> result1
    [['a', '=', 'b'], '->', [['c', '=', 'd'], '&', ['e', '=', 'f']]]
    >>> formula = "forall x: exists y: true -> true & true | ~ true"
    >>> print(ply_parse(formula))
    ['forall', 'x', ['exists', 'y', ['true', '->', [['true', '&', 'true'], '|', ['~', 'true']]]]]
    >>> formula = "~ true | true & true -> forall x: exists y: true"
    >>> print(ply_parse(formula))
    [[['~', 'true'], '|', ['true', '&', 'true']], '->', ['forall', 'x', ['exists', 'y', 'true']]]
    >>> formula = "true & forall x: x = x"
    >>> print(ply_parse(formula))
    ['true', '&', ['forall', 'x', ['x', '=', 'x']]]
    >>> formula = "true & (forall x: x = x)" # same as previous
    >>> print(ply_parse(formula))
    ['true', '&', ['forall', 'x', ['x', '=', 'x']]]
    >>> formula = "forall x: x = x & true"
    >>> print(ply_parse(formula))
    ['forall', 'x', [['x', '=', 'x'], '&', 'true']]
    >>> formula = "(forall x: x = x) & true" # different to previous
    >>> print(ply_parse(formula))
    [['forall', 'x', ['x', '=', 'x']], '&', 'true']
    >>> formula = "forall x: = x & true"
    >>> print(ply_parse(formula))
    Syntax error, line 2: EQUALS
    []
    """
    keywords = {"exists": "EXISTS", "forall": "FORALL",
                "true": "TRUE", "false": "FALSE"}
    tokens = (["SYMBOL", "COLON", "COMMA", "LPAREN", "RPAREN",
               "EQUALS", "NOT", "AND", "OR", "IMPLIES"] +
              list(keywords.values()))

    def t_SYMBOL(t):
        r"[a-zA-Z]\w*"
        t.type = keywords.get(t.value, "SYMBOL")
        return t

    t_EQUALS = r"="
    t_NOT = r"~"
    t_AND = r"&"
    t_OR = r"\|"
    t_IMPLIES = r"->"
    t_COLON = r":"
    t_COMMA = r","
    t_LPAREN = r"\("
    t_RPAREN = r"\)"

    t_ignore = " \t\n"

    def t_newline(t):
        r"\n+"
        t.lexer.lineno += len(t.value)

    def t_error(t):
        line = t.value.lstrip()
        i = line.find("\n")
        line = line if i == -1 else line[:i]
        raise ValueError("Syntax error, line {0}: {1}"
                         .format(t.lineno + 1, line))

    def p_formula_quantifier(p):
        """FORMULA : FORALL SYMBOL COLON FORMULA
                   | EXISTS SYMBOL COLON FORMULA"""
        p[0] = [p[1], p[2], p[4]]

    def p_formula_binary(p):
        """FORMULA : FORMULA IMPLIES FORMULA
                   | FORMULA OR FORMULA
                   | FORMULA AND FORMULA"""
        p[0] = [p[1], p[2], p[3]]

    def p_formula_not(p):
        "FORMULA : NOT FORMULA"
        p[0] = [p[1], p[2]]

    def p_formula_boolean(p):
        """FORMULA : FALSE
                   | TRUE"""
        p[0] = p[1]

    def p_formula_group(p):
        "FORMULA : LPAREN FORMULA RPAREN"
        p[0] = p[2]

    def p_formula_symbol(p):
        "FORMULA : SYMBOL"
        p[0] = p[1]

    def p_formula_equals(p):
        "FORMULA : TERM EQUALS TERM"
        p[0] = [p[1], p[2], p[3]]

    def p_term(p):
        """TERM : SYMBOL LPAREN TERMLIST RPAREN
                | SYMBOL"""
        p[0] = p[1] if len(p) == 2 else [p[1], p[3]]

    def p_termlist(p):
        """TERMLIST : TERM COMMA TERMLIST
                    | TERM"""
        p[0] = p[1] if len(p) == 2 else [p[1], p[3]]

    def p_error(p):
        if p is None:
            raise ValueError("Unknown error")
        raise ValueError("Syntax error, line {0}: {1}".format(
            p.lineno + 1, p.type))

    # from lowest to highest precedence!
    precedence = (("nonassoc", "FORALL", "EXISTS"),
                  ("right", "IMPLIES"),
                  ("left", "OR"),
                  ("left", "AND"),
                  ("right", "NOT"),
                  ("nonassoc", "EQUALS"))

    lexer = ply.lex.lex()
    parser = ply.yacc.yacc()
    try:
        return parser.parse(text, lexer=lexer)
    except ValueError as err:
        print(err)
        return []


def main():
    if len(sys.argv) == 1 or len(sys.argv) > 2 or \
                    sys.argv[1] in {'-h', '--help'}:
        print('Usage: {} <file>.flo'.format(sys.argv[0]))
        sys.exit()

    fh = get_file_handle(sys.argv[1])
    ply_parse(fh.read())


if __name__ == '__main__':
    import doctest
    doctest.testmod()