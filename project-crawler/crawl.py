import argparse
import json
import os
import re
import timeit

import anytree
import anytree.exporter
import humanize
import magic
import numpy

from datetime import datetime
from git.cmd import Git

from utils import print_stage, pp
from source_inspector import SourceInspector


def path_to_string(node):
    crumbs = [n.name for n in node.path]
    return '/'.join(crumbs)

def aggregate_data(node):
    node.easy_path = path_to_string(node)
    if node.is_leaf:
        return {
            'source_files': 1,
            'sloc_count': node.meta.get('sloc', 0),
            'value_count' : node.value,
            'bytes_count' : node.meta.get('size', 0),
        }
    else:
        counter = {
            'source_files': 0,
            'sloc_count': 0,
            'value_count' : 0,
            'bytes_count' : 0,
        }
        for c in node.children:
            partial_counter = aggregate_data(c)
            for k in counter:
                counter[k] += partial_counter[k]
        node.counter = counter
        return node.counter

def make_tree_path(root, path):
    current = root
    for child in path.split(os.sep):
        partial = next((cc for cc in current.children if cc.name == child), None)
        if partial:
            current = partial
        else:
            current = anytree.Node(child, parent=current)
    return current

def inspect_git_history(git, root):
    def remove_root_name(path):
        return os.sep.join(path.split(os.sep)[1:])

    module_paths = {remove_root_name(node.easy_path):node for node in root.leaves}

    change_history = git.whatchanged('--oneline').split('\n')
    change_entry = re.compile(r':\d{6} \d{6} \w+ \w+ \w+\t([^\t]+)(?:\t([^\t]+))?')
    commit_count = 0

    for change in change_history:
        if change.startswith(':'):
            file_change = change_entry.search(change)
            if file_change:
                filepath = file_change.group(1)
                new_filepath = file_change.group(2)

                if new_filepath and new_filepath in module_paths:
                    module_paths[filepath] = module_paths[new_filepath]

                if filepath in module_paths:
                    node = module_paths[filepath]
                    if hasattr(node, 'temperature'):
                        node.temperature += 1
                    else:
                        node.temperature = 1

            else:
                print( '***', change )
                raise ValueError("Cannot parse commit change.")
        else:
            commit_count += 1

    for k in module_paths:
        node = module_paths[k]
        if not hasattr(node, 'temperature'):
            raise ValueError(f'Module {node.name} does not appear in change log.')

    return commit_count

def parse_git_repository(src_root, output=None):
    project_name = os.path.basename(src_root)
    print_stage(f'Inspecting {project_name}')

    git = Git(src_root)
    git_filelist = sorted(git.ls_files().split('\n'), key=lambda s : s.count(os.sep))
    root = anytree.Node(project_name)

    for filepath in git_filelist:
        folder = os.path.dirname(filepath)
        file = os.path.basename(filepath)
        sherlock = SourceInspector(os.path.join(src_root,filepath))

        if not sherlock.is_code:
            continue

        if folder:
            parent = make_tree_path(root, folder)
        else:
            parent = root

        print('.', end='')
        sherlock.inspect()
        meta = sherlock.metadata()
        node = anytree.Node(file, parent=parent, value=meta['cognitive_complexity'], meta=meta)

    aggregate_data(root)
    codebase_size = root.counter['bytes_count']
    print(f'\nCompleted scan of {root.counter["source_files"]} files or {humanize.naturalsize(codebase_size)} of code.')

    print('Digesting coupling information...')
    SourceInspector.resolve_imports(root)

    print('Inspecting git history...')
    commit_count = inspect_git_history(git, root)
    print(f'Completed analysis of {commit_count} commits.')

    if not output:
        output = f'{project_name}.json'
    exporter = anytree.exporter.JsonExporter(indent=4, sort_keys=True)
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

    parse_git_repository(os.path.abspath(args.root), output=args.output)


if __name__ == '__main__':
    duration = timeit.timeit(main, number=1)
    now = datetime.now().strftime('%H:%M:%S')
    print_stage(f'[{now}] Finished in {duration:.2f} seconds.')
