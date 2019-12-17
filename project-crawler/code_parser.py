from datetime import datetime
from utils import print_stage
import os
import re
import timeit


def remove_cpp_comments(text):
    return re.sub('//.*?\n|/\*.*?\*/', '', text, flags=re.S)

def parse_cpp_imports(source_code):
    source_wihtout_comments = remove_cpp_comments(source_code)

    local_ref = re.compile(r'\s*#include\s*\"([/\w\.\-\+]+)\"\s*')
    extern_ref = re.compile(r'\s*#include\s*<([/\w\.\-\+]+)>\s*')

    local_includes = local_ref.findall(source_wihtout_comments)
    extern_includes = extern_ref.findall(source_wihtout_comments)

    return { 'local': local_includes, 'extern': extern_includes }


def parse_java_imports(source_code):
    source_wihtout_comments = remove_cpp_comments(source_code)

    package_ref = re.compile(r'\s*package\s+([\w\.]+)\s*')
    package = package_ref.findall(source_wihtout_comments)
    assert(len(package) == 1)
    package = '.'.join(package[0].split('.')[:3])

    import_refs = re.compile(r'\s*import\s+([\w\.]+)\s*')
    imports = import_refs.findall(source_wihtout_comments)

    local_imports = [i for i in imports if i.startswith(package)]
    extern_imports = [i for i in imports if not i.startswith(package)]

    return { 'local': local_imports, 'extern': extern_imports, 'package': package }

def parse_swift_imports(source_code):
    source_wihtout_comments = remove_cpp_comments(source_code)
    
    import_refs = re.compile(r'\s*import\s+(?:(?:typealias|struct|class|enum|protocol|let|var|func)\s+)?([/\w\.\-\+]+)\s*')
    imports = import_refs.findall(source_wihtout_comments)

    return { 'local': imports }


def main():
    sourcefile = "./data/identify.cpp"
    with open(sourcefile, "rt") as src:
        content = src.read()
    print(parse_cpp_imports(content))

    sourcefile = "./data/LoginActivity.kt"
    with open(sourcefile, "rt") as src:
        content = src.read()
    print(parse_java_imports(content))

    sourcefile = "./data/BluetoothManager.swift"
    with open(sourcefile, "rt") as src:
        content = src.read()
    print(parse_swift_imports(content))


if __name__ == '__main__':
    duration = timeit.timeit(main, number=1)
    now = datetime.now().strftime('%H:%M:%S')
    print_stage(f'[{now}] Finished in {duration:.2f} seconds.')
