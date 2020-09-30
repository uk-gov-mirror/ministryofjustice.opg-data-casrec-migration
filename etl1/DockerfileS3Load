FROM python:3.7-slim
RUN  apt-get update
RUN apt-get install -y build-essential
RUN apt-get install -y libpq-dev
RUN pip3 install boto3
COPY ./load_s3_local.py /load_s3_local.py
CMD ["echo", "NO_OP"]
