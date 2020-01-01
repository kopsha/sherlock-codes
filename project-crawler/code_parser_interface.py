import abc

class CodeParserInterface(metaclass=abc.ABCMeta):
    """Interface definition for code parsing"""

    @property
    def supported_extensions(self):
        return self._supported_extensions

    @abc.abstractmethod
    def remove_comments_and_literals(self): pass

    @abc.abstractmethod
    def count_effective_lines_of_code(self): pass

    # @abstractmethod
    # def compute_nested_complexity(self): pass

    # @abstractmethod
    # def compute_decision_complexity(self): pass

    # @abstractmethod
    # def parse_imports(self): pass

if __name__ == '__main__':
    print(f'{__file__} is a true module, you can only import it.')
