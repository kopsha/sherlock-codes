import argparse
import json
import os
import re
import timeit

import anytree
import anytree.exporter
import humanize
import magic

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
        meta['imports'] = code_parser.parse_java_imports(source_code)
    elif meta.get('extension') in ['.swift']:
        meta['imports'] = code_parser.parse_swift_imports(source_code)
    elif meta.get('extension') in ['.py']:
        meta['imports'] = code_parser.parse_python_imports(source_code)
    else:
        pass

    meta['aggregate_complexity'] = sum([
        meta.get('nested_complexity') or 1,
        meta.get('decision_complexity'),
        len(meta.get('imports', {}).get('local', [])),
    ])

    return meta['aggregate_complexity']


def parse_git_repository(src_root, output=None):

    def aggregate_data(node):
        if not node.children:
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

    if not output:
        output = f'{project_name}.json'
    exporter = anytree.exporter.JsonExporter(indent=4, sort_keys=True)
    with open(output, "wt") as out:
        exporter.write(root, out)

    # dependency data
    module_names = sorted([node.name for node in anytree.PreOrderIter(root, filter_=lambda n: not n.children)])
    modules = [node for node in anytree.PreOrderIter(root, filter_=lambda n: not n.children)]
    dependency_data = {}

    for i, module in enumerate(sorted(modules, key=lambda m: m.name)):
        depends = [0] * len(modules)
        imports = module.meta.get('imports')
        if imports:
            for import_name in imports['local']:
                name = os.path.basename(import_name)
                if name in module_names:
                    ndx = module_names.index(name)
                    depends[ndx] = 1
        dependency_data[module.name] = depends.copy()

    # TODO: add dependency data to project json
    # for k in dependency_data:
    #     print(f'"{k}" : {dependency_data[k]},')

    print_stage('Changed together log')
    change_log = []
    whatchanged = git.whatchanged().split('\n')
    whatchanged.reverse()

    pick_path = re.compile(r':\d{6} \d{6} \w+ \w+ \w+\s+(\S+)')
    last_commit = []
    commit_count = 0
    for line in whatchanged:
        if line.startswith(':'):
            lookup = pick_path.search(line)
            if lookup:
                rel_path = str(lookup.group(1))
                rel_name = os.path.basename(rel_path)
                last_commit.append(rel_name)
            else:
                print( '***', line )
        elif line.startswith('commit'):
            for this in last_commit:
                if this in module_names:
                    # build all pairs
                    pairs = [(this,other) for other in last_commit if other != this and other in module_names]
                    change_log.extend(pairs)
            last_commit = []
            commit_count += 1

    from collections import Counter
    limit = max(int(commit_count / 100.0), 13)
    together = Counter(change_log).most_common()

    # TODO: add change coupling data to project json
    for pair, count in together:
        change_coupling = count*100/commit_count
        if change_coupling >= 10:
            print(f'{pair} are changing together {change_coupling:.1f} % of the time.')

    highest_change = max([c for p,c in together])*100/commit_count
    print(f'Analyzed {commit_count} commits and found highest change rate {highest_change:.1f} %.')

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
