# build stage
FROM python:3.11 AS builder-deps
ARG OPTIONAL_DEPENDENCIES_GROUPS

# install PDM
RUN pip install -U pip setuptools wheel
RUN pip install pdm

# copy files
COPY pyproject.toml pdm.lock /project/

# install dependencies first so that the image does not change unless dependencies change
WORKDIR /project
RUN mkdir __pypackages__ && pdm sync --prod --no-editable --no-self -G :all

FROM builder-deps AS builder
COPY src/ /project/src
RUN pdm sync --prod --no-editable -G :all

# run stage
FROM python:3.11 AS final

RUN mkdir /etc/opa/

# retrieve packages from build stage
ENV PYTHONPATH=/project/pkgs
COPY --from=builder /project/__pypackages__/3.11/lib /project/pkgs

# retrieve executables
COPY --from=builder /project/__pypackages__/3.11/bin/* /bin/

COPY settings.toml /etc/opa/
