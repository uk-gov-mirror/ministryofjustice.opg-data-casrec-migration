FROM python:3.8-slim
RUN  apt-get update
RUN apt-get install -y build-essential
RUN apt-get install -y libpq-dev
RUN apt-get install -y postgresql-client
COPY ./requirements.txt /requirements.txt
RUN pip3 install -r requirements.txt
COPY ./app /app
WORKDIR app
RUN chmod 755 run_rationalise.sh
RUN chmod 755 app.py
CMD ["tail", "-f", "/dev/null"]
