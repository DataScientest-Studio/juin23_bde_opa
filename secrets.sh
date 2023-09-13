#!/bin/bash

SECRETS_DIR=app_data/secrets

check_secret_exists() {
    local file_path="$1"
    local error_message="$2"

    if ! [ -f "$file_path" ]; then
        echo "${error_message}"
        exit 1
    fi
}

check_all_secrets_exist() {
    declare -A secrets=(
        ["fmp_cloud_api_key"]="a FMP Cloud API key (you can subscribe at https://fmpcloud.io/login)"
        ["mongodb_root_username"]="an username for mongo DB root"
        ["mongodb_root_password"]="a password for mongo DB root (Strong passwords can be generated using e.g. 'openssl rand -base64 20')"
        ["mongodb_username"]="an username for mongo DB user"
        ["mongodb_password"]="a password for mongo DB user (Strong passwords can be generated using e.g. 'openssl rand -base64 20')"
        ["data_report_api_username"]="an username to authorize API access to data report"
        ["data_report_api_password"]="a password to authorize API access to data report"
    )

    # Check that all secrets are present
    for secret in "${!secrets[@]}"; do
        file_path="${SECRETS_DIR}/${secret}"
        check_secret_exists "${SECRETS_DIR}/${secret}" "Error: ${file_path} should contain ${secrets[$secret]}"
    done
}

if [ "$0" = "$BASH_SOURCE" ]; then
    check_all_secrets_exist
    echo "All secrets are available"
fi
