# OPA Project

## Requirements

The project must have a `secrets` directory

## Running it

`docker-compose up`.

## Force rebuild

By default the docker-compose won't rebuild the images even though the code may have changed.

`docker-compose up --force-recreate --build`

## Run locally

First execute `./setup-local.sh`

Run the financial data reader with : `python -m financial_data_reader`
