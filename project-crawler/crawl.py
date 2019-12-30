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

from utils import print_stage
import code_parser

def quick_look(filepath):
    meta = {}
    filepath = os.path.realpath(filepath)
    filename,ext = os.path.splitext(filepath)
    meta['name'] = os.path.basename(filename)
    meta['extension'] = ext
    meta['is_code'] = False

    if os.path.isdir(filepath):
        meta['is_directory'] = True     # possibly a submodule
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

    if meta['mime'].startswith('text'):
        meta['is_code'] = any([
            'script' in meta['mime'],
            'text/x-' in meta['mime'],
            meta['extension'] in extra_source_extension
        ])

    return meta


def compute_decision_complexity(source_code):
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

    found = decisions.findall(source_code)
    count = len(found)

    return count


def risk_assesment(meta):

    def print_risks(points, risks):
        if (risks):
            for r in risks: print(f'*** {r}')
            print(f'*** risk points: {points}')

    risks = []
    points = 0

    sloc = meta.get('sloc', 0)
    if 300 <= sloc < 500:
        risks.append('[info] Arguably many lines of code, this may be ok for now.')
        points += 2
    elif 500 <= sloc < 1000:
        risks.append('[warning] Quite many lines of code, plan on refactoring.')
        points += 5
    elif 1000 <= sloc:
        risks.append('[error] Way too many lines of code, refactoring is required.')
        points += 8

    decisions = meta.get('decision_complexity', 0)
    if 40 <= decisions < 60:
        risks.append('[info] Arguably many decisions, it is ok if it makes other files less complicated.')
        points += 5
    elif 60 <= decisions < 100:
        risks.append('[warning] Quite many decisions, consider adding more unit tests and review the entire file.')
        points += 8
    elif 100 <= decisions:
        risks.append('[error] Way too many decisions, full code coverage is required.')
        points += 13

    nested = meta.get('nested_complexity', 0)
    if 8 <= nested < 13:
        risks.append('[warning] Quite many nested code blocks, most of the code is in the right half of the screen.')
        points += 5
    elif 13 <= nested:
        risks.append('[error] Way too many nested code blocks, all of the code is off the screen.')
        points += 8

    print_risks(points, risks)

    return (points, risks)


def inspect(filepath, meta):

    print(f'Scanning {meta.get("name")}{meta.get("extension")}')

    filepath = os.path.realpath(filepath)
    with open(filepath, 'rt') as source_file:
        source_code = source_file.read()

    # TODO: remove comments based on extension
    clean_source_code = code_parser.remove_cpp_comments_and_literals(source_code)

    blank_lines = 0
    effective_lines = 0
    all_lines = 0
    for line in clean_source_code.split('\n'):
        all_lines += 1
        if line.strip():
            effective_lines += 1
        else:
            blank_lines += 1

    meta['loc'] = all_lines
    meta['sloc'] = effective_lines
    meta['blank_lines'] = blank_lines

    meta['nested_complexity'] = code_parser.parse_nested_blocks(clean_source_code)
    meta['decision_complexity'] = compute_decision_complexity(clean_source_code)

    meta['risks_points'],meta['risks'] = risk_assesment(meta)

    if meta.get('extension') in ['.h', '.cpp', '.mm', '.hpp', '.c', '.cc']:
        meta['imports'] = code_parser.parse_cpp_imports(source_code)
    elif meta.get('extension') in ['.java', '.kt']:
        meta['imports'],meta['package'] = code_parser.parse_java_imports(source_code)
    elif meta.get('extension') in ['.swift']:
        meta['imports'] = code_parser.parse_swift_imports(source_code)
    elif meta.get('extension') in ['.py']:
        meta['imports'] = code_parser.parse_python_imports(source_code)
    else:
        pass

    meta['aggregate_complexity'] = sum([
        meta.get('nested_complexity') or 1,
        meta.get('decision_complexity'),
        len(meta.get('imports', [])),
    ])

    return meta['aggregate_complexity']


def parse_git_repository(src_root, output=None):

    def path_to_string(node):
        crumbs = [n.name for n in node.path]
        return '/'.join(crumbs)

    def aggregate_data(node):
        node.easy_path = path_to_string(node)
        if node.is_leaf:
            return {
                'source_files': 1,
                'sloc_count': node.meta.get('sloc'),
                'risks_count' : len(node.meta.get('risks')),
                'value_count' : node.value,
                'bytes_count' : node.meta.get('size'),
            }
        else:
            counter = {
                'source_files': 0,
                'sloc_count': 0,
                'risks_count' : 0,
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

    project_name = os.path.basename(src_root)
    print_stage(f'Analyzing {project_name}')

    git = Git(src_root)
    git_filelist = sorted(git.ls_files().split('\n'), key=lambda s : s.count(os.sep))
    root = anytree.Node(project_name)

    for filepath in git_filelist:
        folder = os.path.dirname(filepath)
        file = os.path.basename(filepath)
        file_meta = quick_look(os.path.join(src_root,filepath))

        if not file_meta.get('is_code'):
            continue

        if folder:
            parent = make_tree_path(root, folder)
        else:
            parent = root

        value = inspect(os.path.join(src_root,filepath), file_meta)
        node = anytree.Node(file, parent=parent, value=value, meta=file_meta)

    # Count items up
    aggregate_data(root)
    data_bytes = root.counter['bytes_count']
    print(f'Completed scan of {root.counter["source_files"]} files or {humanize.naturalsize(data_bytes)} of code.')

    print('Processing imports...')
    resolver = anytree.Resolver()

    package_map = {}
    for node in root.leaves:
        pkg = node.meta.get('package')
        if pkg:
            refs = package_map.get(pkg, [])
            refs.append(node.easy_path)
            package_map[pkg] = refs

    local_packages = list(set(package_map))

    for m in root.leaves:
        imports = m.meta.get('imports', [])
        local_imports = set()
        libraries = set()
        for import_item in imports:
            if import_item.count(os.sep) < 1:
                # look in siblings
                local_nodes =  anytree.search.findall_by_attr(m.parent, import_item)
                if local_nodes:
                    # add all nodes
                    chk = [x.easy_path for x in local_nodes if x.is_leaf]
                    if not chk:
                        chk = [x.easy_path for x in local_nodes[-1].leaves]
                    assert chk
                    local_imports.update(chk)
                else:
                    # look in the entire project
                    local_nodes = anytree.search.findall_by_attr(root, import_item)
                    if local_nodes:
                        chk = [x.easy_path for x in local_nodes if x.is_leaf]
                        if not chk:
                            chk = [x.easy_path for x in local_nodes[-1].leaves]
                        assert chk
                        local_imports.update(chk)
                    else:
                        libraries.add(import_item)
            else:
                # TODO: resolve relative paths (../)
                package = import_item
                was_found = False
                while package.count('/') >= 3:
                    package,symbol = os.path.split(package)
                    if package in local_packages:
                        found_local = [x for x in package_map[package] if symbol in x]
                        if found_local:
                            local_imports.add(found_local[0])
                        else:
                            local_imports.add( package_map[package][0] )  # :()
                        was_found = True
                        break
                if not was_found:
                    libraries.add(import_item)
                    if import_item.startswith('com/specialized'):
                        print('**** ', m.name, 'imports', import_item, 'but cannot be resolved inside project, is this a library?')

        m.meta['imports'] = list(local_imports)
        m.meta['libraries'] = list(libraries)

    print('Inspecting git history...')

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

    print(f'Analyzed {commit_count} commits.')
    for k in sorted(module_paths):
        node = module_paths[k]
        if not hasattr(node, 'temperature'):
            raise ValueError(f'Module {node.name} does not appear in change log.')

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
