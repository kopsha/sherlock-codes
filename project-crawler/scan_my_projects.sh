#!/bin/bash
set -e

python crawl.py -r ~/src/entr
#python crawl.py -r ~/src/optimal-transaction-hunter
python crawl.py -r ~/src/sherlock-codes

python crawl.py -r ~/wrk/alber/bloks
python crawl.py -r ~/wrk/alber/gui
python crawl.py -r ~/wrk/alber/gui-lcd

python crawl.py -r ~/wrk/turbo-connect-core
python crawl.py -r ~/wrk/turbo-connect-android-lib
python crawl.py -r ~/wrk/turbo-connect-ios-lib
python crawl.py -r ~/wrk/mission-control

mv *.json ../visual-inspector/data
