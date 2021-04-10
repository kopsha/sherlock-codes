#!/bin/bash
set -e

start_webserver()
{
    echo "Starting the web server."
    cd ./visual-inspector
    python render_inspector.py
    cd ./html/
    python -m http.server
    cd ../../
}

crawl()
{
	echo "crawl() invoked with '$@'"
    export PYTHONDONTWRITEBYTECODE=true
    export DEBUG=true
    #find . -name "*.py" | entr -r pytest -v
    cd project-crawler
    python crawl.py
    cd ..
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
        start | webserver) start_webserver ;;
        crawl) crawl $@ ;;
        check | test) run_all_tests ;;
        help) show_usage_instructions ;;
        *) start_webserver ;;
    esac
}

main $@
