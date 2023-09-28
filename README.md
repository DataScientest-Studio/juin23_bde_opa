# OPA Project

[![unit tests](https://github.com/DataScientest-Studio/juin23_bde_opa/actions/workflows/tests_unit.yml/badge.svg)](https://github.com/DataScientest-Studio/juin23_bde_opa/actions/workflows/tests_unit.yml) [![formatting](https://github.com/DataScientest-Studio/juin23_bde_opa/actions/workflows/format.yml/badge.svg)](https://github.com/DataScientest-Studio/juin23_bde_opa/actions/workflows/format.yml)

## What is this ?

This project was developed as part of my [3-month Data Engineer course at Datascientest](https://datascientest.com/formation-data-engineer), in parallel to the pedagogical cursus (which covers topics from Machine Learning essentials to Kubernetes, via SQL, MongoDB, Scala, Spark,...).

It basically consists of :

* Retrieving stock market data at regular intervals,
* Storing it in a local database,
* Making it available through an HTTP API (see it [live](http://141.145.219.241:8000/docs)),
* Displaying the data in a dashboard (see it [live](http://141.145.219.241:8050/)),
* Putting all that in production, microservices-style

Please note that the project is hosted on a free VM which slows down the response time at least by a factor of 2.

See a full technical report (aimed at the pedagogical team) [here](docs/report/opa.pdf).

A demonstration of the project was made to the pedagogical team in late September 2023, with [some slides](https://jherve.github.io/opa/presentation/) that were presented along a [scripted demo](docs/presentation/do_demo.sh) that can be run in a terminal.

## Running the project

1. Use helper script `./secrets.sh` to fill the `app_data/secrets` with the application's secrets. By the end it should have the following structure :

    ```
    app_data/secrets
    ├── fmp_cloud_api_key
    ├── mongodb_root_username
    ├── mongodb_root_password
    ├── mongodb_username
    └── mongodb_password
    ```

1. Run `docker compose up -d`

On a cold start (especially if the database needs to be created), some services might timeout. In this case, simply executing step 2 again should solve the issue.

You will get :

* A stock values dashboard on : http://localhost:8050
* A JSON API to retrieve stock values on : http://localhost:8000/ (with docs on : http://localhost:8000/docs)
* A MongoDB server accessible via mongodb://{mongodb_username}:{mongodb_password}@localhost:27117

## Development commands

For convenience during development, a commodity script `run_local.sh` can execute the following parts of the application directly on the local machine : 

* `financial_data_reader` (the part in charge of reading the external API)
* `data_report` (the dashboard)
* `internal_api` (the local API)

It can also execute those common tasks :

* `format` (to format the code)
* `static_analysis` (for type checking with mypy)
* `shell` (a IPython shell to run some parts of the application)
* `mongosh` (to run a shell on the database)
* `make_report` (to generate PDF/html reports)

It can also run tests (see next paragraph).

From the root directory of the project, simply run `./run_local.sh` for help.

Please not that it relies on the [pdm](https://pdm.fming.dev/) Python package and dependency manager for execution.

### Local installation using `pdm`

The `opa` package can simply be installed using `pdm install`

### Local installation within a virtual environment

Please run the following steps in your favorite shell :

```
python -m venv ${LOCAL_VENV}
source ${LOCAL_VENV}/bin/activate

pip install --upgrade pip
pip install -e .[storage,data_report,financial_reader,api]
```

Local commands can now be executed. Please check the source of `./run_local.sh` to see the various commands available (and copy the commands as-is by deleting `pdm run`).

## Running tests

Several types of tests have been implemented (not to a 100% test coverage) :

1. functional (run against a live version of the application)
1. integration (run against a live test database)
1. unit (run in isolation with mock components)

### Via Docker containers

Simply run `docker compose up --profile test`

### On the local machine

Tests can be run using `run_local.sh` script :

* `./run_local.sh test_unit`
* `./run_local.sh test_integration`
* `./run_local.sh test_functional`

## Miscellaneous

### Force rebuild of docker images

The docker compose doesn't rebuild the images even though the code may have changed. This command can be a lifesaver in situations that are unexpected : `docker compose up --force-recreate --build`
