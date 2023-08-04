FROM python:3.11
ARG OPTIONAL_DEPENDENCIES_GROUPS

# install PDM
RUN pip install -U pip setuptools wheel
RUN pip install pdm

# copy files
COPY pyproject.toml pdm.lock README.md MANIFEST.in /project/
COPY src/ /project/src

# install dependencies and project into the local packages directory
WORKDIR /project
RUN mkdir __pypackages__ && pdm install --no-editable -d -G ${OPTIONAL_DEPENDENCIES_GROUPS}

COPY tests/ /project/tests
