#!/bin/bash

source ./secrets.sh

usage() {
    echo "Command-line helper to run the most common commands in the local environment"
    echo
    echo "Usage: $0 <command>"
    echo "<command> is either a service, a utility, or a test command"
    echo
    echo "  * Services  : internal_api | data_report | financial_data_reader"
    echo "  * Utilities : shell | mongosh | static_analysis | format"
    echo "  * Tests     : test_unit | test_integration | test_functional"
    echo
    echo "For example : '${0} static_analysis'"
}

# Check the number of arguments
if [ $# -ne 1 ]; then
    usage
    exit 1
fi

command="$1"
shift

check_all_secrets_exist

case "$command" in
internal_api)
    pdm run uvicorn opa.api:app --port 8000 --reload
    ;;

data_report)
    pdm run python -m opa.data_report
    ;;

financial_data_reader)
    OPA_USE_HTTP_CACHE=1 pdm run python -m opa.financial_data_reader
    ;;

shell)
    OPA_USE_HTTP_CACHE=1 pdm run python -m opa.shell
    ;;

mongosh)
    mongo_password=$(pdm run dynaconf -i opa.config.settings get secrets.mongodb_password)
    mongo_username=$(pdm run dynaconf -i opa.config.settings get secrets.mongodb_username)

    mongo_url="mongodb://${mongo_username}:${mongo_password}@database:27017"
    docker compose run -it --rm database mongosh "${mongo_url}"
    ;;

static_analysis)
    pdm run mypy src
    ;;

format)
    pdm run black src tests
    ;;

make_report)
    asciidoctor-web-pdf docs/opa.adoc
    ;;

test_unit)
    pdm run pytest tests/unit
    ;;

test_integration)
    OPA_MONGO_DATABASE=stock_market-test pdm run pytest tests/integration
    ;;

test_functional)
    docker compose up -d
    pdm run pytest tests/functional
    ;;

*)
    echo "Unknown command ${command} cannot be run in local."
    usage
    exit 1
    ;;
esac
