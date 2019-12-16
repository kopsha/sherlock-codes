from datetime import datetime
from utils import print_stage
import timeit

import pyparsing as pp

def tick(t):
    print(f'* {t}')


def main():
    source_file = 'data/identify.cpp'
    print_stage(f'Scanning {source_file}')


    g = pp.Forward()

    # nestedParens = nest('(', ')')
    # nestedBrackets = nest('[', ']')
    nestedCurlies = pp.nestedExpr('{', '}').setParseAction(tick)
    #nest_grammar = nestedParens | nestedBrackets | nestedCurlies
    nest_grammar = nestedCurlies

    parens = "(){}[]"
    letters = ''.join([x for x in pp.printables
                       if x not in parens])
    word = pp.Word(letters)

    xxx = pp.OneOrMore(word | nest_grammar)
    xxx.ignore(pp.cppStyleComment)
    xxx.ignore(pp.dblQuotedString)

    for token in xxx.parseFile(source_file):
        print(len(token))


if __name__ == '__main__':
    duration = timeit.timeit(main, number=1)
    now = datetime.now().strftime('%H:%M:%S')
    print_stage(f'[{now}] Finished in {duration:.2f} seconds.')
