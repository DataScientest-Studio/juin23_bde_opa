FROM python:3.11
ARG OPTIONAL_DEPENDENCIES_GROUPS

# install PDM
RUN pip install -U pip setuptools wheel
RUN pip install pdm

# copy files
COPY pyproject.toml pdm.lock README.md MANIFEST.in /project/

# install dependencies first so that the image does not change unless dependencies change
WORKDIR /project
RUN mkdir __pypackages__ && pdm sync --prod --no-editable --no-self -G ${OPTIONAL_DEPENDENCIES_GROUPS}

# install project
COPY src/ /project/src
RUN pdm sync --prod --no-editable -G ${OPTIONAL_DEPENDENCIES_GROUPS}

COPY tests/ /project/tests
