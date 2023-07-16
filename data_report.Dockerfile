FROM python:3

WORKDIR /usr/src/app

COPY requirements-data_report.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python", "-m", "data_report" ]
