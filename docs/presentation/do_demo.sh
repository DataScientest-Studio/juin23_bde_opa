#!/bin/bash
set -u

MONGO_USER=$(head app_data/secrets/mongodb_username)
MONGO_PASSWORD=$(head app_data/secrets/mongodb_password)
MONGO_HOST=localhost
MONGO_PORT=27117
MONGO_DATABASE=stock_market-dev
MONGO_URL=mongodb://${MONGO_USER}:${MONGO_PASSWORD}@${MONGO_HOST}:${MONGO_PORT}/${MONGO_DATABASE}

FMP_CLOUD_API_KEY=$(head app_data/secrets/fmp_cloud_api_key)

API_HOST=localhost
API_PORT=8000
API_USERNAME="julien"
API_PASSWORD="julien"

# Utility functions

function not_installed {
    echo "$1 is not installed"
    exit 1
}

function check_dependencies {
    which http >/dev/null || not_installed httpie
    which mongosh >/dev/null || not_installed mongosh
    which pv >/dev/null || not_installed pv
}

function pe_mongosh {
    pe "mongosh ${MONGO_URL} --authenticationDatabase admin --eval '$1' --quiet"
}

function pe_http {
    url=$1
    opts=${2-}
    params=${3-}
    pe "http -b --pretty=all $opts $url $params 2>/dev/null | less -R"
}

function pe_fmp {
    path=$1
    ticker=$2
    params=${3-}
    pe_http "https://fmpcloud.io/api/v3/$path/$ticker" "" "apikey==${FMP_CLOUD_API_KEY} $params"
}

function pe_api_anonymous {
    path=$1
    pe_http "http://${API_HOST}:${API_PORT}/$path"
}

function pe_api_logged {
    path=$1
    params=${2-}
    pe_http "http://${API_HOST}:${API_PORT}/$path" "--auth ${API_USERNAME}:${API_PASSWORD} --auth-type basic" "$params"
}

# Demo functions

function demo_ext_api {
    # Get data from external API

    # Simple daily data, with a long range
    pe_fmp "historical-price-full" "AAPL" "serietype==line"
    # OHLC coarse-grained range
    pe_fmp "historical-price-full" "AAPL"
    # OHLC fine-grained
    pe_fmp "historical-chart/15min" "AAPL"
}

function demo_reader {
    # Start the database
    pe "docker compose up -d database"
    pe "docker compose up financial_data_reader"

    # Now there are some values
    pe_mongosh "db.stock_values.find({ticker: \"MSFT\", open: {\$exists: 0}}, {}, {limit: 5})"
    pe_mongosh "db.stock_values.find({ticker: \"META\", open: {\$exists: 1}}, {}, {limit: 5})"

    # Can make some other queries
    pe_mongosh "db.stock_values.find({ date: {\$gt: new Date(\"2023-09-20\")} }, {}, {limit: 5})"
}

function demo_internal_api {
    pe "docker compose up -d internal_api"

    # This will not work
    pe_api_anonymous "tickers"

    # This works
    pe_api_logged "tickers"
    pe_api_logged "MSFT" "kind==simple limit==10"
    pe_api_logged "META" "kind==ohlc limit==10"
}

function demo_dashboard {
    pe "docker compose up -d data_report"
}

function demo_tests {
    p "docker compose --profile=test up test_unit"
    docker compose --profile=test up test_unit --force-recreate

    p "docker compose --profile=test up test_integration"
    docker compose --profile=test up test_integration --force-recreate

    p "docker compose --profile=test up test_functional"
    docker compose --profile=test up test_functional --force-recreate
}

check_dependencies

. $(dirname $0)/demo-magic.sh
TYPE_SPEED=100

clear

demo_ext_api
demo_reader
demo_internal_api
demo_dashboard
demo_tests
