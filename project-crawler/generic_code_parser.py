from datetime import datetime
from utils import print_stage

import ast
import os
import re
import timeit

class SherlockScanner:
    """Generic Code Analysis
    It takes in a filepath, raises exception if it's not a valid file
    Runs all checks known to man
    And returns the right metadata
    """

    def __init__(self, path, meta):
        self.meta = meta
        self.messages = None
        self.clean_source_code = None

        self.filepath = os.path.realpath(path)
        with open(self.filepath, 'rt') as source_file:
            source_code = source_file.read()


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


def run_self_check():
    scanner = SherlockScanner('something', meta={})
    pass


if __name__ == '__main__':
    duration = timeit.timeit(run_self_check, number=1)
    now = datetime.now().strftime('%H:%M:%S')
    print_stage(f'[{now}] Finished in {duration:.2f} seconds.')
