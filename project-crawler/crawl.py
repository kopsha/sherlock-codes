import argparse
import re
import timeit
import os

import anytree
import anytree.exporter
import magic
import clang.cindex

from datetime import datetime
from git.cmd import Git

def print_stage(text):
    row_size=80
    filler=' '*(row_size-4-len(text))
    print(f"{'*'*row_size}");
    print(f"* {text}{filler} *")
    print(f"{'*'*row_size}");


def quick_look(filepath):
    meta = {}
    filepath = os.path.realpath(filepath)
    filename,ext = os.path.splitext(filepath)
    meta['name'] = os.path.basename(filename)
    meta['extension'] = ext

    if os.path.isdir(filepath):
        meta['is_directory'] = True     # possibly a submodule
        meta['is_code'] = False
        return meta

    mage = magic.Magic(mime=True, mime_encoding=True) 
    meta['mime'] = mage.from_file(filepath)
    meta['type'] = magic.from_file(filepath)

    meta['size'] = os.path.getsize(filepath)

    extra_source_extension = [
        '.swift',
        '.kt',
        '.sh'
    ]
    meta['is_code'] = False

    if meta['mime'].startswith('text'):
        meta['is_code'] = any([
            'script' in meta['mime'],
            'text/x-' in meta['mime'],
            meta['extension'] in extra_source_extension
        ])

    return meta

# global for better speed
cpp_parser = clang.cindex.Index.create()
def parse_cpp(filepath):

    cpp_pool = set()

    translate_decl = {
        clang.cindex.CursorKind.CLASS_DECL : "class",
        clang.cindex.CursorKind.STRUCT_DECL : "struct",
        clang.cindex.CursorKind.UNION_DECL : "union",
        clang.cindex.CursorKind.FUNCTION_DECL : "function",
        clang.cindex.CursorKind.FUNCTION_TEMPLATE : "function template",
        clang.cindex.CursorKind.CLASS_TEMPLATE : "class template",
        clang.cindex.CursorKind.CLASS_TEMPLATE_PARTIAL_SPECIALIZATION : "class template specialization",
    }

    def explore_tree(node, current_file):
        try:
            kind = node.kind
        except ValueError as e:
            print('Silenced Error:', e)
            kind = clang.cindex.CursorKind.UNEXPOSED_DECL

        if kind in translate_decl:
            name_only,ext = os.path.splitext(node.location.file.name)
            current_name_only,ext = os.path.splitext(current_file)
            if name_only == current_name_only:
                cpp_pool.add(f'{translate_decl[kind]} {node.spelling}')

        for c in node.get_children():
            explore_tree(c, filepath)


    cpp_pool = set()
    translation_unit = cpp_parser.parse(filepath, options=clang.cindex.TranslationUnit.PARSE_INCOMPLETE|clang.cindex.TranslationUnit.PARSE_SKIP_FUNCTION_BODIES)
    explore_tree(translation_unit.cursor, filepath)

    return list(cpp_pool)


def compute_indentation(effective_lines, tab_size=4):
    # find deepest indentation
    indent_capture = re.compile(r'^(\s*)')
    tabs = re.compile(r'(\t)')
    max_indentation = 0
    for line in effective_lines:
        indentation = indent_capture.match(line)
        assert(indentation)
        spaced_indentation = tabs.sub(' '*tab_size, indentation.group(1))
        max_indentation = max(len(spaced_indentation), max_indentation)
    max_indentation = max_indentation // tab_size
    return max_indentation


def compute_decision_complexity(effective_lines):
    markers = [
        'elif',
        'for',
        'guard',
        'if',
        'repeat',
        'switch',
        'try',
        'until',
        'when',
        'while',
    ]
    decisions = re.compile(r'(?:^|\W)('+'|'.join(markers)+')(?:$|\W)')

    count = 0
    for line in effective_lines:
        found = decisions.findall(line)
        count += len(found)

    return count


def inspect(filepath, meta):
    print(f'Scanning {meta.get("name")}{meta.get("extension")}')
    filepath = os.path.realpath(filepath)
    with open(filepath, 'rt') as source_file:
        source_code = source_file.read()

    source_lines = source_code.splitlines()
    meta['loc'] = len(source_lines)

    blank_lines = 0
    effective_lines = []
    is_line_comment = re.compile(r'\s*(//|#).*')

    for line in source_lines:
        if line.strip():
            if is_line_comment.match(line):
                blank_lines += 1
            else:
                effective_lines.append(line)
        else:
            blank_lines += 1

    meta['sloc'] = len(effective_lines)
    meta['blank_lines'] = blank_lines
    assert(meta['loc'] == (meta['sloc'] + meta['blank_lines']))

    meta['easy_complexity'] = compute_indentation(effective_lines)
    meta['decision_complexity'] = compute_decision_complexity(effective_lines)

    if meta.get('extension') in ['.cpp', '.cxx']:
        meta['exports'] = parse_cpp(filepath)

    meta['aggregate_complexity'] = sum([
        meta.get('easy_complexity') or 1,
        len(meta.get('exports', [])),
        meta.get('decision_complexity'),
    ])

    return meta['aggregate_complexity']


def parse_git_repository(src_root, output=None):

    def make_path(root, path):
        current = root
        for child in path.split(os.sep):
            partial = next((cc for cc in current.children if cc.name == child), None)
            if partial:
                current = partial
            else:
                current = anytree.Node(child, parent=current)
        return current

    project_name = os.path.basename(src_root)
    print_stage(f'Analyzing {project_name}')

    if not output:
        output = f'{project_name}.json'

    git = Git(src_root)

    root = anytree.Node(project_name)
    resolver = anytree.Resolver()
    parent = root

    for filepath in sorted(git.ls_files().split('\n'), key=lambda s : s.count(os.sep)):
        folder = os.path.dirname(filepath)
        file = os.path.basename(filepath)
        
        file_meta = quick_look(f'{src_root}/{filepath}')

        if not file_meta.get('is_code'):
            # we are interested only in source files
            continue

        if not folder:
            parent = root
        else:
            try:
                parent = resolver.get(root, f'{folder}')
            except anytree.ChildResolverError:
                parent = make_path(root, folder)

        value = inspect(f'{src_root}/{filepath}', file_meta)
        node = anytree.Node(file, parent=parent, value=value, meta=file_meta)

    exporter = anytree.exporter.JsonExporter(indent=4)
    with open(output, "wt") as out:
        exporter.write(root, out)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-r', '--root', required=True, help='git repository root')
    parser.add_argument('-o', '--output', help='name of the output json')
    args = parser.parse_args()

    if not os.path.isdir(args.root):
        print(f'Error: the {args.root} is not a directory.')
        return -1

    parse_git_repository(args.root, output=args.output)


if __name__ == '__main__':
    duration = timeit.timeit(main, number=1)
    now = datetime.now().strftime('%H:%M:%S')
    print_stage(f'[{now}] Finished in {duration:.2f} seconds.')
