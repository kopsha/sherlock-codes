from datetime import datetime
from utils import print_stage

import ast
import os
import re
import timeit

class CodeScanner(object):
    """Generic CodeScanner
    It takes in a filepath
    Runs all checks known to man
    And returns the right metadata
    """

    def __init__(self):
        self.do_not_keep = None

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
    pass


if __name__ == '__main__':
    duration = timeit.timeit(run_self_check, number=1)
    now = datetime.now().strftime('%H:%M:%S')
    print_stage(f'[{now}] Finished in {duration:.2f} seconds.')
