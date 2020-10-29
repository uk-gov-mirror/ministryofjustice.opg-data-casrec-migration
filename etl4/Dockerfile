FROM python:3.8-slim
RUN  apt-get update
RUN apt-get install -y build-essential
RUN apt-get install -y libpq-dev
COPY ./requirements.txt /requirements.txt
RUN pip3 install -r requirements.txt
COPY ./__init__.py /__init__.py
COPY ./config.py /config.py
COPY ./load.py /load.py
RUN chmod 755 *.py
CMD ["echo", "NO_OP"]
