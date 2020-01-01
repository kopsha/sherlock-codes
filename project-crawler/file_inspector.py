from datetime import datetime
from utils import print_stage, pp

import os
import re
import timeit


class FileInspector:
    """Generic Code Analysis
    It takes in a filepath
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
        self.path = os.path.realpath(path)
        self.is_code = False

        self.is_directory = os.path.isdir(self.path)
        if self.is_directory:
            self.messages.append(f'The provided {path} is a directory, analysis will be skipped.')
            return

        self.filename = os.path.basename(self.path)
        self.name,self.extension = os.path.splitext(self.filename)
        self.size = os.path.getsize(self.path)

        self.is_code = self.extension in FileInspector.supported_extensions

        self.messages = []
        self._source_code = None

    def inspect(self):
        self._source_code = None

        if not self.is_code:
            self.messages.append(f'{self.extension} inspection is not supported.')
            return

        with open(self.path, 'rt') as source_file:
            self._source_code = source_file.read()

        # TODO: create parser based on extension

    def metadata(self):
        meta = {k:v for k,v in vars(self).items() if not k.startswith('_')}
        return meta


def run_self_check():
    src_folder = './testdata'
    source_files = [fn for fn in os.listdir(src_folder)]

    for file in source_files:
        parser = FileInspector(os.sep.join([src_folder, file]))
        parser.inspect()
        pp(parser.metadata(), pretext=file)


if __name__ == '__main__':
    duration = timeit.timeit(run_self_check, number=1)
    now = datetime.now().strftime('%H:%M:%S')
    print_stage(f'[{now}] Finished in {duration:.2f} seconds.')
