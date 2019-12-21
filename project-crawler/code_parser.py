from datetime import datetime
import os
import re
import timeit

from utils import print_stage

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

        if any([line_comment, block_comment, string_literal]):
            if c1 == '\n':   # keep newlines
                clean_source.append(c1)
            continue

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

        clean_source.append(c1)

    clean_source.append(source_code[-1])

    return ''.join(clean_source)


def parse_cpp_imports(source_code):
    local_ref = re.compile(r'\s*?#(?:include|import)\s*\"([/\w\.\-\+]+)\"\s*?')
    extern_ref = re.compile(r'\s*?#(?:include|import)\s*<([/\w\.\-\+]+)>\s*?')

    local_includes = local_ref.findall(source_code)
    extern_includes = extern_ref.findall(source_code)

    return { 'local': local_includes, 'extern': extern_includes }


def parse_java_imports(source_code):
    package_ref = re.compile(r'\s*package\s+([\w\.]+)\s*')
    package = package_ref.findall(source_code)
    if len(package) < 1:
        package = ''
    else:
        assert( len(package) == 1 )
        package = '.'.join(package[0].split('.')[:3])

    import_refs = re.compile(r'\s*?import\s+([\w\.]+)\s*?')
    imports = import_refs.findall(source_code)

    local_imports = [i for i in imports if i.startswith(package)]
    extern_imports = [i for i in imports if not i.startswith(package)]

    return { 'local': local_imports, 'extern': extern_imports, 'package': package }


def parse_swift_imports(source_code):
    import_refs = re.compile(r'\s*?import\s+(?:(?:typealias|struct|class|enum|protocol|let|var|func)\s+)?([/\w\.\-\+]+)\s*?')
    imports = import_refs.findall(source_code)

    return { 'local': imports }


def main():

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
        else:
            print(f'Unknown extension {ext}')


if __name__ == '__main__':
    duration = timeit.timeit(main, number=1)
    now = datetime.now().strftime('%H:%M:%S')
    print_stage(f'[{now}] Finished in {duration:.2f} seconds.')
