#!/bin/bash
set -e

crawl()
{
    out="./out/$2"
	echo "crawl will write to ${out}"
    python crawl.py -r ./root -o $out
}

run_all_tests()
{
    echo "(not defined yet) Running all tests."
    export APP_TEST_MODE=true
    pytest -v
}

show_usage_instructions()
{
    echo "./$(basename $0) says: I help those who help themselves."
}

try_exec()
{
    echo "trying '$@'"
    command=$@
    $command
}

main()
{
    arg="$1"
    case ${arg} in
        crawl) crawl $@ ;;
        check | test) run_all_tests ;;
        help) show_usage_instructions ;;
        *) try_exec $@ ;;
    esac
}

main $@
