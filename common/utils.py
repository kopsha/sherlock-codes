import pprint

def print_stage(text, row_size=80):
    """Pretty banner stage printing helper"""
    filler=' '*(row_size-4-len(text))
    print(f"{'*'*row_size}");
    print(f"* {text}{filler} *")
    print(f"{'*'*row_size}");


def pp(x, pretext=None):
    pp = pprint.PrettyPrinter(indent=4)

    if pretext:
        print(f'{pretext} >>>')

    pp.pprint(x)

    if pretext:
        print(f'<<<')

if __name__ == '__main__':
    print(f'{__file__} is a pure python module, import it.')
