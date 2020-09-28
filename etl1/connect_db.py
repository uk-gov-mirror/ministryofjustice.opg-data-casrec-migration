import os
import boto3
from sqlalchemy import create_engine


def list_bucket_contents(bucket_name, s3_session):
    s3 = s3_session.client("s3")
    resp = s3.list_objects_v2(Bucket=bucket_name)

    files_in_bucket = []

    for obj in resp["Contents"]:
        files_in_bucket.append(obj["Key"])
        print(obj["Key"])
    return files_in_bucket


password = os.environ["DB_PASSWORD"]
db_host = os.environ["DB_HOST"]
port = os.environ["DB_PORT"]
name = os.environ["DB_NAME"]

DATABASES = {
    "casrec-migration": {
        "NAME": name,
        "USER": "casrec",
        "PASSWORD": password,
        "HOST": db_host,
        "PORT": port,
    },
}

bucket_name = "casrec-migration-development"

# choose the database to use
db = DATABASES["casrec-migration"]

# construct an engine connection string
engine_string = "postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}".format(  # pragma: allowlist secret
    user=db["USER"],
    password=db["PASSWORD"],
    host=db["HOST"],
    port=db["PORT"],
    database=db["NAME"],
)

print("Attempting to connect to DB")
engine = create_engine(engine_string)

check_exists_statement = "SELECT * FROM information_schema.tables;"
results = engine.execute(check_exists_statement)

print(f"Results from test query\n\n")
for r in results:
    print(r)

s3_session = boto3.session.Session()

for file in list_bucket_contents(bucket_name, s3_session):
    print(file)
