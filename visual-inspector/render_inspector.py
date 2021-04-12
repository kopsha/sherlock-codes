import argparse
import os
import shutil
import timeit

from datetime import datetime

import jinja2


def render_inspector_pages(data_folder, out_folder):
    print('Rendering templates')

    datafiles = sorted([f for f in os.listdir(data_folder) if f.endswith('.json')])
    env = jinja2.Environment(loader=jinja2.FileSystemLoader('./'))
    pages = [
        env.get_template('index.html'),
        env.get_template('heatmap.html'),
        env.get_template('coupling.html'),
        env.get_template('sunburst.html'),
    ]

    for page in pages:
        output = os.path.join(out_folder, page.name)
        print(f'Writing {output}')
        with open(output, "wt") as out:
            out.write(page.render(datafiles=datafiles))

    print('Copying data files')
    for f in datafiles:
        src = os.path.join(data_folder, f)
        dst = os.path.join(out_folder, f)
        shutil.copyfile(src, dst)

    print('Copying source files')
    src_files = [f for f in os.listdir('./') if f.endswith('.js') or f.endswith('.css')]
    for f in src_files:
        src = os.path.join('./', f)
        dst = os.path.join(out_folder, f)
        print(f'{src} -> {dst}')
        shutil.copyfile(src, dst)

    print('Copying lib files')
    lib_files = [f for f in os.listdir('./static_lib') if f.endswith('.js')]
    for f in lib_files:
        src = os.path.join('./static_lib/', f)
        dst = os.path.join(out_folder, f)
        print(f'{src} -> {dst}')
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

    render_inspector_pages(args.data, args.output)


if __name__ == '__main__':
    duration = timeit.timeit(main, number=1)
    now = datetime.now().strftime('%H:%M:%S')
    print(f'[{now}] Finished in {duration:.2f} seconds.')
