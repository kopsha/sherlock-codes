#!/usr/bin/env bash

repo_path=$(readlink -fn "$1")
if [ -z $repo_path ]; then
    printf "'$1' is not a valid repository.\n"
    exit -1
fi

project=$(basename "$repo_path")
docker run -e PYTHONUNBUFFERED=1 -v "$repo_path":/main/root -v $(pwd)/data:/main/out sherlock-crawler crawl $project

printf "done, moving '$project.json' to visual inspector\n"
mv "$(pwd)/data/$project.json" ../visual-inspector/data/
