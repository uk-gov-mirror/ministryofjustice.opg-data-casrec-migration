FROM python:3.7-slim
RUN  apt-get update
RUN apt-get install -y build-essential
RUN apt-get install -y libpq-dev
RUN pip3 install sqlalchemy psycopg2 boto3 localstack-client pandas
COPY ./casrec_load.py /casrec_load.py
CMD ["python3", "casrec_load.py"]
