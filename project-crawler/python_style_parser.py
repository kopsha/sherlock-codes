from code_parser_interface import CodeParserInterface

import ast
import os
import re

class PythonStyleParser(CodeParserInterface):
    def __init__(self):
        self._supported_extensions = [
            '.py',
        ]
        self._decision_markers = [
            'assert',
            'elif'
            'else',
            'except'
            'for',
            'if',
            'try',
            'while',
            'with',
        ]

    def remove_comments_and_literals(self, source_code, messages):
        if len(source_code) <= 3:
            return source_code

        source_triples = list(zip(source_code[:-2], source_code[1:-1], source_code[2:]))

        clean_source = []
        line_comment = False
        string_literal = False
        literal_started = None
        skip = 0

        for i, (c1, c2, c3) in enumerate(source_triples):
            if skip > 0:
                skip -= 1
                continue

            # end conditions
            if line_comment:
                if c1 == '\n':
                    line_comment = False
                    clean_source.append(c1)
                    continue
            elif string_literal:
                if c1 == '\\':
                    skip = 1    # escaped char follows
                    continue
                assert(len(literal_started) == 1 or len(literal_started) == 3)
                if len(literal_started) == 1:
                    if c1 == literal_started[0]:
                        string_literal = False
                        literal_started = None
                        continue
                else:
                    if c1 == literal_started[0] and c2 == literal_started[1] and c3 == literal_started[2]:
                        string_literal = False
                        literal_started = None
                        skip = 2
                        continue

            # skip any comments
            if any([line_comment, string_literal]):
                if c1 == '\n':   # keep newlines
                    clean_source.append(c1)
                continue

            # start conditions
            if c1 == "'" and c2 == "'" and c3 == "'":   # triple quotes
                string_literal = True
                literal_started = "'''"
                skip = 2
                continue
            elif c1 == '"' and c2 == '"' and c3 == '"': # triple double-quotes
                string_literal = True
                literal_started = '"""'
                skip = 2
                continue
            elif c1 == "'":   # single quote
                string_literal = True
                literal_started = "'"
                continue
            elif c1 == '"':   # double quote
                string_literal = True
                literal_started = '"'
                continue
            elif c1 == "#":
                line_comment = True
                continue

            # valid code
            clean_source.append(c1)

        clean_source.append(source_code[-2])
        clean_source.append(source_code[-1])
        return ''.join(clean_source)

    def compute_nested_complexity(self, source_code, messages):
        has_whitespace = re.compile(r'^(\s*)\S')
        replace_tabs = re.compile(r'\t')
        deep = 0
        deepest = 0
        levels = [0]
        for line_no,line in enumerate(source_code.split('\n')):
            found_spaces = has_whitespace.match(line)
            if found_spaces:
                whitespace = replace_tabs.sub('    ', found_spaces.group(1))
                level = len(whitespace)
                if level > levels[-1]:
                    deep += 1
                    levels.append(level)
                    deepest = max(deep, deepest)
                elif level < levels[-1]:
                    if level in levels:
                        prev = levels.index(level)
                        levels = levels[:prev+1]
                        deep = len(levels)-1
                    else:
                        messages.append(f'[error] Unindent does not match any outer indentation level on line {line_no}.')

        if 8 <= deepest < 13:
            messages.append('[warning] Quite many nested code blocks, most of the code is in the right half of the screen.')
        elif 13 <= deepest:
            messages.append('[error] Way too many nested code blocks, all of the code is off the screen.')

        return deepest

    def compute_decision_complexity(self, source_code, messages):
        decisions = re.compile(r'(?:^|\W)('+'|'.join(self.decision_markers)+')(?:$|\W)')
        found = decisions.findall(source_code)
        decision_count = len(found)

        if 40 <= decision_count < 60:
            messages.append('[info] Arguably many decisions, it is ok if it makes other files less complicated.')
        elif 60 <= decision_count < 100:
            messages.append('[warning] Quite many decisions, consider adding more unit tests and review the entire file.')
        elif 100 <= decision_count:
            messages.append('[error] Way too many decisions, full code coverage is required.')

        return decision_count

    def parse_imports(self, source_code, messages):
        module = ast.parse(source_code)
        imports = []
        for node in module.body:
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                imports.append(node.module)

        return imports

    def resolve_imports(self, root):
        """Resolve imports related to supported extensions"""
        source_nodes = [n for n in root.leaves if n.meta.get('extension') in self.supported_extensions]
        modules = {src.meta.get('name'):src.easy_path for src in source_nodes}

        for node in source_nodes:
            imports = node.meta.get('imports', [])
            local_imports = set()
            libraries = set()
            for import_item in imports:
                if import_item in modules:
                    local_imports.add(modules[import_item])
                else:
                    libraries.add(import_item)

            node.meta['imports'] = sorted(list(local_imports))
            node.meta['libraries'] = sorted(list(libraries))


if __name__ == '__main__':
    print(f'{__file__} is a true module, you can only import it.')
