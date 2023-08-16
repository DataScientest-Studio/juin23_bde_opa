# OPA Project

[![unit tests](https://github.com/DataScientest-Studio/juin23_bde_opa/actions/workflows/tests_unit.yml/badge.svg)](https://github.com/DataScientest-Studio/juin23_bde_opa/actions/workflows/tests_unit.yml) [![formatting](https://github.com/DataScientest-Studio/juin23_bde_opa/actions/workflows/format.yml/badge.svg)](https://github.com/DataScientest-Studio/juin23_bde_opa/actions/workflows/format.yml)

## Run with Docker Compose

Once the secrets are installed (see next paragraph), services can be started using a simple : `docker compose up -d`.

The dashboard will be available on http://localhost:8050

The API documentation will be available on http://localhost:8000/docs

## Secrets

The app secrets are kept within a `app_data/secrets` directory whose content is not versioned for obvious reasons.

It should contain the following files :

```
app_data/secrets
├── fmp_cloud_api_key
├── mongodb_root_username
├── mongodb_root_password
├── mongodb_username
└── mongodb_password
```

Strong passwords can be generated using e.g. `openssl rand -base64 20`

## Environment variables

`OPA_MONGO_DATABASE` can be used to tweak the name of the MongoDB database to use (defaults to "stock_market-dev").

## Development commands

### Run locally

For development convenience, some parts of the application can be run on the local machine.

#### Using pip

For this, please run the following steps in your favorite shell :

```
python -m venv ${LOCAL_VENV}
source ${LOCAL_VENV}/bin/activate

pip install --upgrade pip
pip install .[storage,data_report,financial_reader,api]
```

The financial data reader can be run with `python -m opa.financial_data_reader`.

The dashboard can be run with `python -m opa.data_report`.

#### Using pdm

The `opa` package can be installed with `pdm install`.

The financial data reader can be run with `pdm run python -m opa.financial_data_reader`.

The dashboard can be run with `pdm run python -m opa.data_report`.

### Running tests

Several types of tests can be run either locally or within a dedicated Docker container :

1. functional (run against a live version of the application)
1. integration (run against a live test database)
1. unit (run in isolation with mock components)

They can be run either via docker-compose : `docker compose up --profile test` or locally :

* `pdm run pytest tests/functional`
* `pdm run pytest tests/integration`
* `pdm run pytest tests/unit`

### Miscellaneous

#### Interactive shell

An interactive shell can be started with `pdm run python -m opa.shell`

#### Run commands on the database

MongoDB shell can be accessed via : `docker compose run -it --rm database mongosh mongodb://username@password:database`

#### Static type analysis

... can be run with `mypy opa`.

#### Force rebuild of docker images

By default the docker compose doesn't rebuild the images even though the code may have changed.

`docker compose up --force-recreate --build`