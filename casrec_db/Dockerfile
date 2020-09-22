FROM python:3.7-slim as csv_injest
RUN  apt-get update
RUN apt-get install -y build-essential
RUN apt-get install -y libpq-dev
RUN pip install pandas
COPY ./setup /setup
COPY ./anon_data /anon_data
RUN mkdir -p sql
WORKDIR ./setup
RUN python3 create_casrec_db_tables.py



FROM postgres:10.11
USER postgres
ENV POSTGRES_DB=casrec
ENV POSTGRES_PASSWORD=casrec
ENV POSTGRES_USER=casrec
COPY --from=csv_injest /sql/ /docker-entrypoint-initdb.d/
ENTRYPOINT ["docker-entrypoint.sh"]
EXPOSE 6666:5432
CMD ["postgres"]
