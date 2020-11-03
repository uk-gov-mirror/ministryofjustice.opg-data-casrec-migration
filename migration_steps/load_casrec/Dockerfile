FROM opg_casrec_migration_base_image:latest
COPY requirements.txt /requirements.txt
RUN pip3 install -r requirements.txt
COPY casrec_load.py /casrec_load.py
CMD ["echo", "NO_OP"]
