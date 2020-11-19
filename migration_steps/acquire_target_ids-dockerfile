FROM opg_casrec_migration_base_image:latest
RUN apt-get install -y postgresql-client
COPY requirements.txt /requirements.txt
RUN pip3 install -r requirements.txt
COPY app /app
WORKDIR app
RUN chmod 755 acquire_target_ids.sh
RUN chmod 755 app.py
RUN chmod 755 fixtures.py
CMD ["tail", "-f", "/dev/null"]
