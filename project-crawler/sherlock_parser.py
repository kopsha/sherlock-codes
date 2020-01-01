import inspect
import sys

from utils import print_stage, static_var, pp

from code_parser_interface import CodeParserInterface
from cpp_style_parser import CppStyleParser

def make_extension_map():
    extensions = {}
    current_module = sys.modules[__name__]
    all_parsers = [
        (name,cls) for name,cls in inspect.getmembers(current_module)
        if inspect.isclass(cls)
            and issubclass(cls, CodeParserInterface)
            and name != 'CodeParserInterface'
    ]

    for name, cls in all_parsers:
        parser = cls()
        for ext in parser.supported_extensions:
            if ext in extensions:
                raise AttributeError(f'Class {name}, redefines an already existing extension.')
            extensions[ext] = parser

    return extensions

@static_var('extension_map', {})
def parser_factory(ext):
    """Create an apropriate parser instance based on extension"""
    if not parser_factory.extension_map:
        parser_factory.extension_map = make_extension_map()

    if ext in parser_factory.extension_map:
        return parser_factory.extension_map[ext]
    else:
        raise ValueError(f'Extension {ext} is not supported')

def self_check():
    print_stage('Self check')
    
    cStyleParser = parser_factory('.cpp')
    another = parser_factory('.mm')

    cStyleParser.remove_comments_and_literals('qwertyuiop', [])
    another.remove_comments_and_literals('qwertyuiop', [])

    pp(parser_factory.extension_map, pretext='Supported extension map')


if __name__ == '__main__':
    print(f'{__file__} is a true module, you can only import it.')
    self_check()
