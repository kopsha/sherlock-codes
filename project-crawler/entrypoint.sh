#!/bin/bash
set -e

crawl()
{
	echo "crawl() invoked with '$@'"
    python crawl.py
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


main()
{
    arg="$1"
    case ${arg} in
        crawl) crawl $@ ;;
        check | test) run_all_tests ;;
        help) show_usage_instructions ;;
        *) help ;;
    esac
}

main $@
