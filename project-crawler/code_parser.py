from datetime import datetime
from utils import print_stage

import ast
import os
import re
import timeit



def parse_swift_imports(source_code):
    import_refs = re.compile(r'\s*?import\s+(?:(?:typealias|struct|class|enum|protocol|let|var|func)\s+)?([/\w\.\-\+]+)\s*?')
    imports = import_refs.findall(source_code)

    return imports

