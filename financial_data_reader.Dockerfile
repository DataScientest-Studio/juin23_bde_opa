FROM python:3

WORKDIR /usr/src/app

COPY requirements-financial_data_reader.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python", "-m", "opa.financial_data_reader" ]
