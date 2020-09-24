FROM python:3.7-slim
RUN  apt-get update
RUN apt-get install -y build-essential
RUN apt-get install -y libpq-dev
RUN pip3 install sqlalchemy psycopg2
COPY ./connect_db.py /connect_db.py
CMD ["python3", "connect_db.py"]
