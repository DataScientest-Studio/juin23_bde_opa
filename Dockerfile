# build stage
FROM python:3.11 AS builder
ARG OPTIONAL_DEPENDENCIES_GROUPS

# install PDM
RUN pip install -U pip setuptools wheel
RUN pip install pdm

# copy files
COPY pyproject.toml pdm.lock README.md MANIFEST.in /project/

# install dependencies first so that the image does not change unless dependencies change
WORKDIR /project
RUN mkdir __pypackages__ && pdm sync --prod --no-editable --no-self -G ${OPTIONAL_DEPENDENCIES_GROUPS}

# install project into the local packages directory
COPY src/ /project/src
RUN pdm sync --prod --no-editable -G ${OPTIONAL_DEPENDENCIES_GROUPS}

# run stage
FROM python:3.11

RUN mkdir /etc/opa/

# retrieve packages from build stage
ENV PYTHONPATH=/project/pkgs
COPY --from=builder /project/__pypackages__/3.11/lib /project/pkgs

# retrieve executables
COPY --from=builder /project/__pypackages__/3.11/bin/* /bin/

COPY settings.toml /etc/opa/
