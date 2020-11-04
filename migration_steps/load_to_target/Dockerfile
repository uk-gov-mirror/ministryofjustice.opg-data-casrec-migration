FROM opg_casrec_migration_base_image:latest
COPY ./requirements.txt /requirements.txt
RUN pip3 install -r requirements.txt
COPY ./__init__.py /__init__.py
COPY ./config.py /config.py
COPY ./load.py /load.py
RUN chmod 755 *.py
CMD ["echo", "NO_OP"]
