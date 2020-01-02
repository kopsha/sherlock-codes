import abc

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
    def count_effective_lines_of_code(self, source_code, messages): pass

    @abc.abstractmethod
    def compute_nested_complexity(self, source_code, messages): pass

    @abc.abstractmethod
    def compute_decision_complexity(self, source_code, messages): pass

    @abc.abstractmethod
    def parse_imports(self, source_code, messages): pass

    @abc.abstractmethod
    def resolve_imports(self, root): pass

    @abc.abstractmethod
    def inspect(self, source_code, messages): pass


if __name__ == '__main__':
    print(f'{__file__} is a true module, you can only import it.')
