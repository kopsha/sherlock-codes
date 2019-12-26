from datetime import datetime
from utils import print_stage

import ast
import os
import re
import timeit


def remove_cpp_comments_and_literals(source_code):
    source_doubles = list(zip(source_code[:-1], source_code[1:]))

    line_comment = False
    block_comment = False
    string_literal = False
    skip = 0

    clean_source = []

    for i, (c1,c2) in enumerate(source_doubles):
        if skip > 0:
            skip -= 1
            continue

        # end conditions
        if line_comment:
            if c1 == '\\' and c2 =='\n':
                # line comments continue on next line
                clean_source.append(c2)
                skip = 1
            if c1 == '\n':
                line_comment = False
                clean_source.append(c1)
                continue
        elif block_comment:
            if c1 == '*' and c2 == '/':
                skip = 1
                block_comment = False
                continue
        elif string_literal:
            if c1 == '\\':
                skip = 1
                continue
            elif c1 == '"':
                string_literal = False
                continue

        # skip any comments
        if any([line_comment, block_comment, string_literal]):
            if c1 == '\n':   # keep newlines
                clean_source.append(c1)
            continue

        # special case, do not touch import directives
        if c1 == '#':
            # read whole line from source_code[i]
            line_ends = source_code.find('\n', i)
            if (line_ends > 0):
                whole_line = source_code[i:line_ends]
                # is it an include or import ?
                if re.match(r'#(?:include|import).+', whole_line):
                    clean_source.extend(whole_line)
                    # skip to the end of line
                    skip = len(whole_line)-1
                    continue

        # start conditions
        if c1 == '/' and c2 == '/':
            line_comment = True
            skip = 1
            continue
        elif c1 == '/' and c2 == '*':
            skip = 1
            block_comment = True
            continue
        elif c1 == '"':
            string_literal = True
            continue

        # valid code
        clean_source.append(c1)

    clean_source.append(source_code[-1])

    return ''.join(clean_source)


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


def parse_cpp_imports(source_code):
    import_ref = re.compile(r'\s*?#(?:include|import)\s*[\"<]([/\w\.\-\+]+)[\">]\s*?')

    imports = import_ref.findall(source_code)
    return imports


def parse_java_imports(source_code):
    import_refs = re.compile(r'\s*?import\s+([\w\.]+)\s*?')
    imports = import_refs.findall(source_code)

    imports_with_path = [p.replace('.', '/') for p in imports]

    return imports_with_path


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


def parse_nested_blocks(source_code):
    open_tag = '{'
    close_tag = '}'
    deepest = 0
    deep = 0

    for c in source_code:
        if c == open_tag:
            deep += 1
            deepest = max(deep, deepest)
        elif c == close_tag:
            deep -= 1

    if deep != 0:
        # TODO: collect risks on each phase
        print('*** [info] Nested blocks are not matched. If you used macro magic you are on your own.')

    return deepest


def test_source_parsing():
    source_files = [fn for fn in os.listdir('./data') if not fn.endswith('.strip')]

    for file in source_files:
        source_file = f'./data/{file}'
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
