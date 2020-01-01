import abc
import inspect
import sys

from utils import print_stage, static_var, pp

class AbstractCodeParser(metaclass=abc.ABCMeta):
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


class CStyleParser(AbstractCodeParser):
    def __init__(self):
        self._supported_extensions = [
            '.cpp', '.c', '.h',
            '.hpp', '.cxx', '.cc',
            '.mm', '.m',
        ]
    
    def remove_comments_and_literals(self):
        print('cstyle remove_comments_and_literals')

    def count_effective_lines_of_code(self):
        print('cstyle count_effective_lines_of_code')        


def make_extensions_map():
    extensions = {}
    current_module = sys.modules[__name__]
    all_parsers = [
        (name,cls) for name,cls in inspect.getmembers(current_module)
        if inspect.isclass(cls)
            and issubclass(cls, AbstractCodeParser)
            and name != 'AbstractCodeParser'
    ]

    for name, cls in all_parsers:
        parser = cls()
        for ext in parser.supported_extensions:
            if ext in extensions:
                raise AttributeError(f'Class {name}, redefines an already existing extension.')
            extensions[ext] = parser

    return extensions

@static_var('all_extensions', {})
def parserFactory(ext):
    """Create an apropriate parser instance based on extension"""
    if not parserFactory.all_extensions:
        parserFactory.all_extensions = make_extensions_map()

    if ext in parserFactory.all_extensions:
        return parserFactory.all_extensions[ext]
    else:
        raise ValueError(f'Extension {ext} is not supported')

def self_check():
    print_stage('Self check')
    
    cStyleParser = parserFactory('.cpp')
    another = parserFactory('.mm')

    cStyleParser.remove_comments_and_literals()
    another.remove_comments_and_literals()

    pp(parserFactory.all_extensions, pretext='Support extension map')


if __name__ == '__main__':
    print(f'{__file__} is a true module, you can only import it. \nSelfcheck:')
    self_check()
