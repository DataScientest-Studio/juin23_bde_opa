# build stage
FROM python:3.11 AS builder
ARG OPTIONAL_DEPENDENCIES_GROUPS

# install PDM
RUN pip install -U pip setuptools wheel
RUN pip install pdm

# copy files
COPY pyproject.toml pdm.lock README.md MANIFEST.in /project/
COPY src/ /project/src

# install dependencies and project into the local packages directory
WORKDIR /project
RUN mkdir __pypackages__ && pdm sync --prod --no-editable -G ${OPTIONAL_DEPENDENCIES_GROUPS}


# run stage
FROM python:3.11

# retrieve packages from build stage
ENV PYTHONPATH=/project/pkgs
COPY --from=builder /project/__pypackages__/3.11/lib /project/pkgs

# retrieve executables
COPY --from=builder /project/__pypackages__/3.11/bin/* /bin/