#!/bin/bash
set -e

start_webserver()
{
    python render_inspector.py
    cd ./html/
    echo "Starting the web server."
    python -m http.server
    cd ../
}

run_all_tests()
{
    echo "(not defined yet) Running all tests."
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
        check | test) run_all_tests ;;
        help) show_usage_instructions ;;
        *) start_webserver ;;
    esac
}

main $@
