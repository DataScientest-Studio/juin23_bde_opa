FROM python:3

ARG REQUIREMENTS_FILE

WORKDIR /usr/src/app

COPY ${REQUIREMENTS_FILE} ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
