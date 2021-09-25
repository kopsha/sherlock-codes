import abc
import re

class CodeParserInterface(metaclass=abc.ABCMeta):
    """Interface definition for sherlock code parser"""

    @property
    def supported_extensions(self):
        return self._supported_extensions

    @property
    def decision_markers(self):
        return self._decision_markers

    @abc.abstractmethod
    def remove_comments_and_literals(self, source_code, messages): pass

    @abc.abstractmethod
    def compute_nested_complexity(self, source_code, messages): pass

    @abc.abstractmethod
    def parse_imports(self, source_code, messages): pass

    @abc.abstractmethod
    def resolve_imports(self, root): pass

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
        elif 500 <= effective_lines < 1000:
            messages.append('[warning] Quite many lines of code, plan on refactoring.')
        elif 1000 <= effective_lines:
            messages.append('[error] Way too many lines of code, refactoring is required.')

        return {
            'loc': all_lines,
            'sloc': effective_lines,
            'blank_lines': blank_lines,
        }

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
