import argparse
import os
import shutil
import timeit

from datetime import datetime
from utils import print_stage

import jinja2


def render_inspector_page(data_folder, out_folder):
    print_stage('Rendering')

    datafiles = [f for f in os.listdir(data_folder) if f.endswith('.json')]

    env = jinja2.Environment(loader=jinja2.FileSystemLoader('./'))
    main_page = env.get_template('index.html')
    output = os.path.join(out_folder, main_page.name)

    print(f'Writing {output}')
    with open(output, "wt") as out:
        out.write(main_page.render(datafiles=datafiles))

    print('Copying data files')
    for f in datafiles:
        src = os.path.join(data_folder, f)
        dst = os.path.join(out_folder, f)
        shutil.copyfile(src, dst)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--data', default='./data', help='the folder with projects metadata')
    parser.add_argument('-o', '--output', default='./html', help='a folder to store the generated html files, default is ./html')
    args = parser.parse_args()

    if not os.path.exists(args.data):
        os.makedirs(args.data)

    if not os.path.exists(args.output):
        os.makedirs(args.output)

    render_inspector_page(args.data, args.output)


if __name__ == '__main__':
    duration = timeit.timeit(main, number=1)
    now = datetime.now().strftime('%H:%M:%S')
    print_stage(f'[{now}] Finished in {duration:.2f} seconds.')
