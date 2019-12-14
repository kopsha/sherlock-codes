import argparse
import re
import timeit
import os

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


def parse_git_repository(path, output):
    git = Git(path)
    repository_name = os.path.basename(path)
    print_stage(f'Analyzing {repository_name}')

    root = Node(repository_name)
    resolver = Resolver()
    parent = root

    for f in sorted(git.ls_files().split(), key=lambda s : s.count(os.sep)):
        folder = os.path.dirname(f)
        file = os.path.basename(f)
        
        if file.startswith('.'):
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

        file_size = os.path.getsize(f'{path}/{f}') >> 8
        node = Node(file, parent=parent, value=file_size or 1)

    exporter = JsonExporter(indent=4)
    with open(output, "wt") as out:
        exporter.write(root, out)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-r', '--root', required=True, help='git repository root')
    parser.add_argument('-o', '--output', required=True, help='output json file')
    args = parser.parse_args()

    if not os.path.isdir(args.root):
        print(f'Error: the {args.root} is not a directory.')
        return -1

    parse_git_repository(args.root, output=args.output)


if __name__ == '__main__':
    duration = timeit.timeit(main, number=1)
    now = datetime.now().strftime('%H:%M:%S')
    print_stage(f'[{now}] Finished in {duration:.2f} seconds.')
