#!/bin/bash

LOCAL_VENV=venv/

python -m venv ${LOCAL_VENV}
source ${LOCAL_VENV}/bin/activate

pip install --upgrade pip
pip install -r requirements-dev.txt
pip install -r requirements-financial_data_reader.txt
pip install -r requirements-data_report.txt
