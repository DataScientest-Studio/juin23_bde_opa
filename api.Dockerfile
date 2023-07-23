FROM python:3

WORKDIR /usr/src/app

COPY requirements-api.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "uvicorn", "opa.api:app", "--host", "0.0.0.0", "--port", "8000", "--reload" ]
