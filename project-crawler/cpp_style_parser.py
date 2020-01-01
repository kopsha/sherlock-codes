from code_parser_interface import CodeParserInterface

class CppStyleParser(CodeParserInterface):
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

if __name__ == '__main__':
    print(f'{__file__} is a true module, you can only import it.')
