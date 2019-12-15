import argparse
import re
import timeit
import os

import anytree
import anytree.exporter
import magic

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

    # find deepest indentation
    capture_indentation = re.compile(r'^(\s*)')
    max_indentation = 0
    for line in effective_lines:
        indentation = capture_indentation.match(line)
        assert(indentation)
        max_indentation = max(len(indentation.group(1)), max_indentation)

    meta['easy_complexity'] = max_indentation >> 2

    return meta['easy_complexity']


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
