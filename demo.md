## Preamble

Go to e.g. https://learn.datascientest.com/lesson/243/715 and start the VM.

* `sudo apt install lnav`
* Remove all dangling Docker images/containers/... : `docker system prune`

### To install PDM

1. `sudo apt install python3.8-venv`
1. `curl -sSL https://pdm.fming.dev/install-pdm.py | python3 -`
1. `export PATH=/home/ubuntu/.local/bin:$PATH`

## Run and build the project from scratch

1. Clone it : `git clone https://github.com/DataScientest-Studio/juin23_bde_opa.git`
1. Copy the secrets : `scp -r app_data/secrets datasciencetest:/tmp/secrets`
1. Run the project : `docker compose up -d`

## Show that something is running

1. Show the open ports : `sudo netstat -tulpn | grep -w tcp`
1. Show the logs `docker compose logs | lnav`

## Connect to the database

1. Use mongodb-compass and connect to `mongodb://user:password@63.35.39.206:27117`
1. Get some values from stock_values, e.g. with : `{ticker: "AAPL", open: {$exists: 0}}` or `{ticker: "AAPL", open: {$exists: 1}}`
1. Show some values from company_infos

## API demonstration

1. Open up the docs : http://63.35.39.206:8000/docs or http://localhost:8000/docs
1. Test the endpoints with various queries

## Dashboard demonstration

1. Open up the dashboard : http://63.35.39.206:8050/
1. Switch companies
1. Switch value types

## Test demonstration

1. Run functional tests with the project running : `docker compose --profile=test up test_functional`
1. From now on the project can be shut down
1. Run unit tests : `docker compose --profile=test up test_unit`
1. Run integration tests : `docker compose --profile=test up test_integration`

### Troubleshooting

Those commands will likely crash with message `Error response from daemon: network XXX not found` if they have been run beforehand AND the project has been taken down with `docker compose down`. Options to circumvent this include :

* Running the commands with `--force-recreate` flag
* Run `docker system prune` before anything
