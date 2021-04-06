FROM opg_casrec_migration_base_image:latest
COPY ./load_s3_local.py /load_s3_local.py
COPY ./synchronise_s3.py /synchronise_s3.py
COPY ./local_s3.sh /local_s3.sh
CMD ["echo", "NO_OP"]
