from datetime import datetime
from utils import print_stage

import ast
import os
import re
import timeit


def remove_python_comments_and_literals(source_code):
    assert(len(source_code) > 3 )
    source_triples = list(zip(source_code[:-2], source_code[1:-1], source_code[2:]))

    clean_source = []
    line_comment = False
    string_literal = False
    literal_started = None
    skip = 0

    for i, (c1, c2, c3) in enumerate(source_triples):
        if skip > 0:
            skip -= 1
            continue

        # end conditions
        if line_comment:
            if c1 == '\n':
                line_comment = False
                clean_source.append(c1)
                continue
        elif string_literal:
            if c1 == '\\':
                skip = 1    # escaped char follows
                continue
            assert(len(literal_started) == 1 or len(literal_started) == 3)
            if len(literal_started) == 1:
                if c1 == literal_started[0]:
                    string_literal = False
                    literal_started = None
                    continue
            else:
                if c1 == literal_started[0] and c2 == literal_started[1] and c3 == literal_started[2]:
                    string_literal = False
                    literal_started = None
                    skip = 2
                    continue

        # skip any comments
        if any([line_comment, string_literal]):
            if c1 == '\n':   # keep newlines
                clean_source.append(c1)
            continue

        # start conditions
        if c1 == "'" and c2 == "'" and c3 == "'":   # triple quotes
            string_literal = True
            literal_started = "'''"
            skip = 2
            continue
        elif c1 == '"' and c2 == '"' and c3 == '"': # triple double-quotes
            string_literal = True
            literal_started = '"""'
            skip = 2
            continue
        elif c1 == "'" and c2 != "'":   # single quote
            string_literal = True
            literal_started = "'"
            continue
        elif c1 == '"' and c2 != '"':   # double quote
            string_literal = True
            literal_started = '"'
            continue
        elif c1 == "#":
            line_comment = True
            continue

        # valid code
        clean_source.append(c1)

    clean_source.append(source_code[-2])
    clean_source.append(source_code[-1])
    return ''.join(clean_source)



def parse_swift_imports(source_code):
    import_refs = re.compile(r'\s*?import\s+(?:(?:typealias|struct|class|enum|protocol|let|var|func)\s+)?([/\w\.\-\+]+)\s*?')
    imports = import_refs.findall(source_code)

    return imports


def parse_python_imports(source_code):
    module = ast.parse(source_code)
    imports = []
    for node in module.body:
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            imports.append(node.module)

    return imports


def test_source_parsing():
    src_folder = './testdata'
    source_files = [fn for fn in os.listdir(src_folder) if not fn.endswith('.strip')]

    for file in source_files:
        source_file = os.sep.join(src_folder, source_file)
        print(f'Processing {source_file}')
        with open(source_file, 'rt') as src:
            source = src.read()

        clean_source = remove_cpp_comments_and_literals(source)

        with open(f'{source_file}.strip', 'wt') as out:
            out.write(clean_source)

        in_cnt = source.count('\n')
        out_cnt = clean_source.count('\n')
        assert(in_cnt == out_cnt)

        filename,ext = os.path.splitext(file)

        if ext in ['.swift']:
            print(parse_swift_imports(clean_source))
        elif ext in ['.kt', '.java']:
            print(parse_java_imports(clean_source))
        elif ext in ['.h', '.cpp', '.mm', '.hpp', '.cc']:
            print(parse_cpp_imports(clean_source))
        elif ext in ['.py']:
            # TODO: there must be a better way
            clean_source = remove_python_comments_and_literals(source)
            with open(f'{source_file}.strip', 'wt') as out:
                out.write(clean_source)
            print(parse_python_imports(source))     # applied on original source code
        else:
            print(f'Unknown extension {ext}')

        print(f'Nested blocks: {parse_nested_blocks(clean_source)}')


def main():
    test_source_parsing()


if __name__ == '__main__':
    duration = timeit.timeit(main, number=1)
    now = datetime.now().strftime('%H:%M:%S')
    print_stage(f'[{now}] Finished in {duration:.2f} seconds.')
