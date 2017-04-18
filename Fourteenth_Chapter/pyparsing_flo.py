#!/usr/bin/python3

import sys
from pyparsing import (Suppress, Word, Group,
                       Forward, Keyword, Literal, opAssoc,
                       delimitedList, ParserElement, operatorPrecedence,
                       alphas, alphanums,
                       ParseException, ParseSyntaxException)
ParserElement.enablePackrat()


def get_text(filename):
    try:
        with open(filename) as fh:
            return fh.read()
    except (EnvironmentError, IOError) as file_err:
        print('Error processing {}: {}'.format(filename, file_err))
        sys.exit()


def pyparse_flo(text):
    left_parenthesis, right_parenthesis, colon = map(Suppress, '():')
    boolean = Keyword('false') | Keyword('true')
    forall = Keyword('forall')
    exists = Keyword('exists')
    and_ = Literal('&')
    or_ = Literal('|')
    not_ = Literal('~')
    equals = Literal('=')
    implies = Literal('->')
    symbol = Word(alphas, alphanums)
    term = Forward()
    term << (Group(symbol + Group(left_parenthesis +
                   delimitedList(term) + right_parenthesis)) | symbol)
    formula = Forward()
    forall_expression = forall + symbol + colon + formula
    exists_expression = exists + symbol + colon + formula
    operand = forall_expression | exists_expression | boolean | term
    formula << operatorPrecedence(operand, [
        (equals, 2, opAssoc.RIGHT),
        (not_, 1, opAssoc.RIGHT),
        (and_, 2, opAssoc.LEFT),
        (or_, 2, opAssoc.LEFT),
        (implies, 2, opAssoc.RIGHT)])

    try:
        result = formula.parseString(text, parseAll=True)
        assert len(result) == 1
        return result[0].asList()
    except (ParseException, ParseSyntaxException) as parse_err:
        print('Syntax Error:\n{}\n{}^'.format(parse_err.line,
                                              ' ' * (parse_err.column -1)))


def main():
    if len(sys.argv) == 1 or len(sys.argv) > 2 or sys.argv[1] in {'-h', '--help'}:
        print('Usage: {} <file>.fls'.format(sys.argv[0]))
        sys.exit()

    text_to_parse = get_text(sys.argv[1])
    blocks_tree = pyparse_flo(text_to_parse)
    return blocks_tree


if __name__ == '__main__':
    main()