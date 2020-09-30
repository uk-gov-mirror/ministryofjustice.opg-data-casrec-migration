import boto3
import os
import logging
from botocore.exceptions import ClientError


def drop_bucket(bucket_name, s3_session):
    s3_res = s3_session.resource(
        "s3",
        endpoint_url="http://localstack:4572",
        aws_access_key_id="fake",
        aws_secret_access_key="fake",
    )
    bucket_to_del = s3_res.Bucket(bucket_name)
    for key in bucket_to_del.objects.all():
        key.delete()
    bucket_to_del.delete()


def create_bucket(bucket_name, s3, region=None):
    """Create an S3 bucket in a specified region

    If a region is not specified, the bucket is created in the S3 default
    region (us-east-1).

    :param bucket_name: Bucket to create
    :param region: String region to create bucket in, e.g., 'us-west-2'
    :return: True if bucket created, else False
    """

    # Create bucket
    try:
        if region is None:
            s3.create_bucket(Bucket=bucket_name)
        else:
            location = {"LocationConstraint": region}
            s3.create_bucket(Bucket=bucket_name, CreateBucketConfiguration=location)
        print("Bucket created")
    except ClientError as e:
        logging.error(e)
        return False
    return True


def upload_file(bucket, file_name, s3, object_name=None):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """

    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = file_name

    # Upload the file

    try:
        s3.upload_file(file_name, bucket, object_name)
    except ClientError as e:
        logging.error(e)
        return False
    print(f"Uploaded {file_name}")
    return True


def list_buckets(s3, region=None):
    # Retrieve the list of existing buckets
    response = s3.list_buckets()

    # Output the bucket names

    print("Existing buckets:")
    buckets = []
    for bucket in response["Buckets"]:
        print(f'  {bucket["Name"]}')
        buckets.append(bucket["Name"])

    return buckets


def list_bucket_contents(bucket_name, s3):
    resp = s3.list_objects_v2(Bucket=bucket_name)

    files_in_bucket = []

    for obj in resp["Contents"]:
        files_in_bucket.append(obj["Key"])
        print(obj["Key"])
    return files_in_bucket


bucket_name = "casrec-migration-local"
region = "eu-west-1"

s3_session = boto3.session.Session()
s3 = s3_session.client(
    "s3",
    endpoint_url="http://localstack:4572",
    aws_access_key_id="fake",
    aws_secret_access_key="fake",
)

bucket_exists = False
for bucket in list_buckets(s3, region):
    if bucket_name == bucket:
        bucket_exists = True
if bucket_exists:
    print("Dropping bucket")
    drop_bucket(bucket_name, s3_session)

print("Creating bucket")
create_bucket(bucket_name, s3, region)

anon_data_dir = "./anon_data"

for file in os.listdir(anon_data_dir):
    file_path = f"{anon_data_dir}/{file}"
    s3_file_path = f"/anon/{file}"
    upload_file(bucket_name, file_path, s3, s3_file_path)

list_bucket_contents(bucket_name, s3)
