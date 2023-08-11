# OPA Project

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