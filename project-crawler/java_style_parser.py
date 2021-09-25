from code_parser_interface import CodeParserInterface
from cpp_style_parser import CppStyleParser

import os
import re
from collections import defaultdict

class JavaStyleParser(CppStyleParser):
    def __init__(self):
        self._supported_extensions = [
            '.java',
            '.kt',
            '.aidl',
        ]

        self._decision_markers = [
            'case',
            'catch'
            'default',
            'else',
            'for',
            'if',
            'switch',
            'try',
            'while',
        ]

    def parse_imports(self, source_code, messages):
        package_ref = re.compile(r'\s*package\s+([\w\.]+)\s*')
        package_decl = package_ref.findall(source_code)
        package = ''
        if (package_decl):
            assert(len(package_decl) == 1)
            package = os.sep.join(package_decl[0].split('.'))

        import_refs = re.compile(r'\s*?import\s*(?:static\s*)?([\w\*\.]+)\s*?')
        imports = import_refs.findall(source_code)

        imports_with_path = [p.replace('.', os.sep) for p in imports]

        return imports_with_path, package

    def resolve_imports(self, root):
        """Resolve imports related to supported extensions"""
        source_nodes = [n for n in root.leaves if n.meta.get('extension') in self.supported_extensions]

        package_map = defaultdict(list)
        for node in source_nodes:
            pkg = node.meta.get('package')
            if pkg:
                package_map[pkg].append(node.easy_path)

        local_packages = list(set(package_map))

        for node in source_nodes:
            imports = node.meta.get('imports', [])
            local_imports = set()
            libraries = set()
            for import_item in imports:
                if import_item.count(os.sep) < 1:
                    # look in siblings
                    raise ValueError(f'Found import without package in {node.name}, source: {import_item}')

                was_resolved = False
                package,symbol = os.path.split(import_item)
                if package in local_packages:
                    package_paths = []
                    if symbol == '*':
                        # take all package files
                        package_paths = [pp for pp in package_map[package]]
                    else:
                        package_paths = [pp for pp in package_map[package] if symbol in pp]
                    
                    if package_paths:
                        local_imports.update(package_paths)
                        was_resolved = True

                if not was_resolved:
                    libraries.add(import_item)
                    # TODO: explicit declaration imports cannot be resolved without parsing

            node.meta['imports'] = sorted(list(local_imports))
            node.meta['libraries'] = sorted(list(libraries))


    def inspect(self, source_code, messages):
        meta = {}
        clean_source_code = self.remove_comments_and_literals(source_code, messages)

        line_stats = self.count_effective_lines_of_code(clean_source_code, messages)
        meta.update(line_stats)

        meta['nested_complexity'] = self.compute_nested_complexity(clean_source_code, messages)
        meta['decision_complexity'] = self.compute_decision_complexity(clean_source_code, messages)
        meta['imports'],meta['package'] = self.parse_imports(source_code, messages)

        meta['cognitive_complexity'] = sum([
            meta.get('nested_complexity') or 1,
            meta.get('decision_complexity'),
            len(meta.get('imports', [])),
        ])

        return meta


if __name__ == '__main__':
    print(f'{__file__} is a true module, you can only import it.')
