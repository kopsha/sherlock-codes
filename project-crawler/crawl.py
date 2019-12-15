import argparse
import re
import timeit
import os

import magic

from datetime import datetime
from git.cmd import Git
from anytree import Node, Resolver, RenderTree, LevelOrderIter
from anytree.exporter import JsonExporter

def print_stage(text):
    row_size=80
    filler=' '*(row_size-4-len(text))
    print(f"{'*'*row_size}");
    print(f"* {text}{filler} *")
    print(f"{'*'*row_size}");


def quick_look(filepath):
    meta = {}

    filename,ext = os.path.splitext(filepath)
    meta['name'] = os.path.basename(filename)
    meta['extension'] = ext

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
            'text/x' in meta['mime'],
            meta['extension'] in extra_source_extension
        ])

    return meta


def inspect(filepath, meta):
    print(f'Scanning {meta.get("name")}{meta.get("extension")}')
    with open(filepath, 'rt') as source_file:
        source_code = source_file.read()

    source_lines = source_code.splitlines()

    return len(source_lines)


def parse_git_repository(src_root, output=None):
    project_name = os.path.basename(src_root)
    print_stage(f'Analyzing {project_name}')

    if not output:
        output = f'{project_name}.json'

    git = Git(src_root)

    root = Node(project_name)
    resolver = Resolver()
    parent = root

    for filepath in sorted(git.ls_files().split(), key=lambda s : s.count(os.sep)):
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
            except Exception as e:
                # parent not found, we must create one
                grandparent_folder = os.path.dirname(folder)
                if not grandparent_folder:
                    # root is the grandparent
                    parent = Node(folder.split(os.sep)[-1], parent=root)
                else:
                    # here, the grandparent must exist in the tree
                    grandparent = resolver.get(root, grandparent_folder)
                    parent = Node(folder.split(os.sep)[-1], parent=grandparent)

        value = inspect(f'{src_root}/{filepath}', file_meta)
        node = Node(file, parent=parent, value=value, meta=file_meta)

    exporter = JsonExporter(indent=4)
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
