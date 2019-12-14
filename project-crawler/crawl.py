import argparse
import re
import timeit
import os

from datetime import datetime
from git.cmd import Git

def print_stage(text):
    row_size=80
    filler=' '*(row_size-4-len(text))
    print(f"{'*'*row_size}");
    print(f"* {text}{filler} *")
    print(f"{'*'*row_size}");


def parse_git_repository(root):
    git = Git(root)
    for f in git.ls_files().split():
        folder = os.path.dirname(f) or '.'
        file = os.path.basename(f)
        print(folder, '/', file)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-r', '--root', required=True, help='git repository root')
    args = parser.parse_args()

    print_stage(f'Analyzing')
    
    if not os.path.isdir(args.root):
        print(f'Error: the {args.root} is not a directory.')
        return -1

    parse_git_repository(args.root)


if __name__ == '__main__':
    duration = timeit.timeit(main, number=1)
    now = datetime.now().strftime('%H:%M:%S')
    print_stage(f'[{now}] Finished in {duration:.2f} seconds.')
