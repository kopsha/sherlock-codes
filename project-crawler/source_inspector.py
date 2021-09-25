from datetime import datetime
from common.utils import print_stage
from pprint import pprint

import os
import re
import timeit

import sherlock_parser

class SourceInspector:
    """Generic Code Analysis
    It takes in a filepath
    Runs all checks known to man
    And returns the right metadata"""

    available_parsers = sherlock_parser.make_extension_map()

    def resolve_imports(root):
        """Forward import resolution call to all available parsers"""
        unique_parsers = set()
        for ext,parser in SourceInspector.available_parsers.items():
            unique_parsers.add(parser)

        for parser in unique_parsers:
            parser.resolve_imports(root)

    def __init__(self, path):
        self._path = os.path.realpath(path)
        self.is_code = False
        self.messages = []

        self.is_directory = os.path.isdir(self._path)
        if self.is_directory:
            self.messages.append(f'The provided {path} is a directory, analysis will be skipped.')
            return

        self.filename = os.path.basename(self._path)
        self.name,self.extension = os.path.splitext(self.filename)
        self.size = os.path.getsize(self._path)

        self.is_code = self.extension in SourceInspector.available_parsers

    def inspect(self):
        if not self.is_code:
            self.messages.append(f'{self.extension} inspection is not supported.')
            return

        with open(self._path, 'rt') as source_file:
            source_code = source_file.read()

        parser = sherlock_parser.parser_factory(self.extension)
        meta = parser.inspect(source_code, self.messages)

        for k,v in meta.items():
            assert not hasattr(self, k)
            setattr(self, k, v)

    def metadata(self):
        meta = {k:v for k,v in vars(self).items() if not k.startswith('_')}
        return meta


def run_self_check():
    src_folder = './testdata'
    source_files = [fn for fn in os.listdir(src_folder)]

    print_stage('available_parsers')
    pprint(SourceInspector.available_parsers)

    print_stage('testdata files')
    for file in source_files:
        parser = SourceInspector(os.sep.join([src_folder, file]))
        parser.inspect()
        print(file)
        pprint(parser.metadata())


if __name__ == '__main__':
    duration = timeit.timeit(run_self_check, number=1)
    now = datetime.now().strftime('%H:%M:%S')
    print_stage(f'[{now}] Finished in {duration:.2f} seconds.')
