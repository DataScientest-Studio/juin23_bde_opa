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

## Run commands on the database

`docker-compose run -it --rm database mongosh mongodb://username@password:database`

## Interactive shell

An interactive shell can be run with `python -m opa.shell`

## Static type analysis

... can be run with `mypy opa`.
