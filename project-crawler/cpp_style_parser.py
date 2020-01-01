from code_parser_interface import CodeParserInterface

import re

class CppStyleParser(CodeParserInterface):
    def __init__(self):
        self._supported_extensions = [
            '.cpp', '.c', '.h',
            '.hpp', '.cxx', '.cc',
            '.mm', '.m',
        ]
    
    def remove_comments_and_literals(self, source_code, messages):
        src_doubles = list(zip(source_code[:-1], source_code[1:]))

        line_comment = False
        block_comment = False
        string_literal = False
        skip = 0

        clean_source = []

        for i, (c1,c2) in enumerate(src_doubles):
            if skip > 0:
                skip -= 1
                continue

            # end conditions
            if line_comment:
                if c1 == '\\' and c2 =='\n':
                    # line comments continue on next line
                    clean_source.append(c2)
                    skip = 1
                if c1 == '\n':
                    line_comment = False
                    clean_source.append(c1)
                    continue
            elif block_comment:
                if c1 == '*' and c2 == '/':
                    skip = 1
                    block_comment = False
                    continue
            elif string_literal:
                if c1 == '\\':
                    skip = 1
                    continue
                elif c1 == '"':
                    string_literal = False
                    continue

            # skip any comments
            if any([line_comment, block_comment, string_literal]):
                if c1 == '\n':   # keep newlines
                    clean_source.append(c1)
                continue

            # special case, do not touch import directives
            if c1 == '#':
                # read whole line from source_code[i]
                line_ends = source_code.find('\n', i)
                if (line_ends > 0):
                    whole_line = source_code[i:line_ends]
                    # is it an include or import ?
                    if re.match(r'#(?:include|import).+', whole_line):
                        clean_source.extend(whole_line)
                        # skip to the end of line
                        skip = len(whole_line)-1
                        continue

            # start conditions
            if c1 == '/' and c2 == '/':
                line_comment = True
                skip = 1
                continue
            elif c1 == '/' and c2 == '*':
                skip = 1
                block_comment = True
                continue
            elif c1 == '"':
                string_literal = True
                continue

            # valid code
            clean_source.append(c1)

        clean_source.append(source_code[-1])

        return ''.join(clean_source)


    def count_effective_lines_of_code(self, source_code, messages):
        blank_lines = 0
        effective_lines = 0
        all_lines = 0
        for line in source_code.split('\n'):
            all_lines += 1
            if line.strip():
                effective_lines += 1
            else:
                blank_lines += 1

        if 300 <= effective_lines < 500:
            messages.append('[info] Arguably many lines of code, this may be ok for now.')
            points += 2
        elif 500 <= effective_lines < 1000:
            messages.append('[warning] Quite many lines of code, plan on refactoring.')
            points += 5
        elif 1000 <= effective_lines:
            messages.append('[error] Way too many lines of code, refactoring is required.')
            points += 8

        return {
            'loc': all_lines,
            'sloc': effective_lines,
            'blank_lines': blank_lines,
        }

    def compute_nested_complexity(self, source_code, messages):
        open_tag = '{'
        close_tag = '}'
        deepest = 0
        deep = 0

        for c in source_code:
            if c == open_tag:
                deep += 1
                deepest = max(deep, deepest)
            elif c == close_tag:
                deep -= 1

        if deep != 0:
            messages.append('[warning] Nested blocks are not matched. If you used macro magic you are on your own.')

        if 8 <= deepest < 13:
            messages.append('[warning] Quite many nested code blocks, most of the code is in the right half of the screen.')
            points += 5
        elif 13 <= deepest:
            messages.append('[error] Way too many nested code blocks, all of the code is off the screen.')
            points += 8

        return deepest

    def compute_decision_complexity(self, source_code, messages):
        markers = [
            'case',
            'catch'
            'default',
            'else',
            'for',
            'foreach',
            'for_each',
            'if',
            'switch',
            'try',
            'while',
        ]
        decisions = re.compile(r'(?:^|\W)('+'|'.join(markers)+')(?:$|\W)')
        found = decisions.findall(source_code)
        decision_count = len(found)

        if 40 <= decision_count < 60:
            messages.append('[info] Arguably many decisions, it is ok if it makes other files less complicated.')
            points += 5
        elif 60 <= decision_count < 100:
            messages.append('[warning] Quite many decisions, consider adding more unit tests and review the entire file.')
            points += 8
        elif 100 <= decision_count:
            messages.append('[error] Way too many decisions, full code coverage is required.')
            points += 13

        return decision_count

    def parse_imports(self, source_code, messages):
        import_ref = re.compile(r'\s*?#(?:include|import)\s*[\"<]([/\w\.\-\+]+)[\">]\s*?')
        imports = import_ref.findall(source_code)
        return imports


    def inspect(self, source_code, messages):
        meta = {}
        clean_source_code = self.remove_comments_and_literals(source_code, messages)

        line_stats = self.count_effective_lines_of_code(clean_source_code, messages)
        meta.update(line_stats)

        meta['nested_complexity'] = self.compute_nested_complexity(clean_source_code, messages)
        meta['decision_complexity'] = self.compute_decision_complexity(clean_source_code, messages)
        meta['imports'] = self.parse_imports(source_code, messages)

        meta['cognitive_complexity'] = sum([
            meta.get('nested_complexity') or 1,
            meta.get('decision_complexity'),
            len(meta.get('imports', [])),
        ])

        return meta

if __name__ == '__main__':
    print(f'{__file__} is a true module, you can only import it.')
