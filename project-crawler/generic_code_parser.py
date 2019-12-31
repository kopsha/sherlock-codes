from datetime import datetime
from utils import print_stage, pp

import os
import re
import timeit
import magic

class SourceParser:
    """Generic Code Analysis
    It takes in a filepath, raises exception if it's not a valid file
    Runs all checks known to man
    And returns the right metadata"""

    supported_extensions = [
        '.cpp', '.c', '.h', '.hpp', '.cxx', '.cc',
        '.mm', '.m',
        '.cs',
        '.swift',
        '.jav', '.java', '.jsp', '.jspx',
        '.kt',
        '.py',
        '.go',
        '.pl',
        '.rb',
        '.js', '.jse', '.asp', '.aspx',
        '.coffee',
        '.php',
        '.jsl',
        '.fs',
        '.as', '.mxml'
        '.sh', '.bat',
    ]

    def __init__(self, path):
        self._clean_source_code = None
        self._meta = {}
        self._messages = []

        self.filepath = os.path.realpath(path)
        with open(self.filepath, 'rt') as source_file:
            source_code = source_file.read()

        self._quick_look()

        # TODO: create parser based on extension

    @property
    def meta(self):
        """Current source metadata.
        It may be incomplete if inspection was not performed"""
        return self._meta

    def remove_comments_and_literals(self):
        pass

    def count_effective_lines_of_code(self):
        pass

    def compute_nested_complexity(self):
        pass

    def compute_decision_complexity(self):
        pass

    def parse_imports(self):
        pass

    def generate_wordcloud(self):
        pass

    def _quick_look(self):
        filename,ext = os.path.splitext(self.filepath)
        self._meta['name'] = os.path.basename(filename)
        self._meta['extension'] = ext

        self.meta['is_code'] = False

        if os.path.isdir(self.filepath):
            self.meta['is_directory'] = True     # possibly a submodule
            return self.meta

        mage = magic.Magic(mime=True, mime_encoding=True) 
        self.meta['mime'] = mage.from_file(self.filepath)
        self.meta['type'] = magic.from_file(self.filepath)

        self.meta['size'] = os.path.getsize(self.filepath)


        if self.meta['mime'].startswith('text'):
            self.meta['is_code'] = any([
                'script' in self.meta['mime'],
                'text/x-' in self.meta['mime'],
                self.meta['extension'] in SourceParser.supported_extensions
            ])

    def inspect(self):
        return self.meta


def run_self_check():
    src_folder = './testdata'
    source_files = [fn for fn in os.listdir(src_folder) if not fn.endswith('.strip')]

    for file in source_files:
        parser = SourceParser(os.sep.join([src_folder, file]))
        pp(parser.inspect(), pretext='inspect meta')


if __name__ == '__main__':
    duration = timeit.timeit(run_self_check, number=1)
    now = datetime.now().strftime('%H:%M:%S')
    print_stage(f'[{now}] Finished in {duration:.2f} seconds.')
