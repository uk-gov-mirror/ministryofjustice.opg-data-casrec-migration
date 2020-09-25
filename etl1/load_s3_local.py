import localstack_client.session
import os
import logging
from botocore.exceptions import ClientError

s3_session = localstack_client.session.Session()


def drop_bucket(bucket_name, s3_session):
    s3 = s3_session.resource("s3")
    bucket_to_del = s3.Bucket(bucket_name)
    for key in bucket_to_del.objects.all():
        key.delete()
    bucket_to_del.delete()


def create_bucket(bucket_name, s3_session, region=None):
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
            s3_client = s3_session.client("s3")
            s3_client.create_bucket(Bucket=bucket_name)
        else:
            s3_client = s3_session.client("s3", region_name=region)
            location = {"LocationConstraint": region}
            s3_client.create_bucket(
                Bucket=bucket_name, CreateBucketConfiguration=location
            )
        print("Bucket created")
    except ClientError as e:
        logging.error(e)
        return False
    return True


def upload_file(bucket, file_name, s3_session, object_name=None):
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
    s3_client = s3_session.client("s3")
    try:
        response = s3_client.upload_file(file_name, bucket, object_name)
        print(response)
    except ClientError as e:
        logging.error(e)
        return False
    print(f"Uploaded {file_name}")
    return True


def list_buckets(s3_session, region=None):
    # Retrieve the list of existing buckets
    s3 = s3_session.client("s3")
    response = s3.list_buckets()

    # Output the bucket names

    print("Existing buckets:")
    buckets = []
    for bucket in response["Buckets"]:
        print(f'  {bucket["Name"]}')
        buckets.append(bucket["Name"])

    return buckets


def list_bucket_contents(bucket_name, s3_session):
    s3 = s3_session.client("s3")
    resp = s3.list_objects_v2(Bucket=bucket_name)

    files_in_bucket = []

    for obj in resp["Contents"]:
        files_in_bucket.append(obj["Key"])
        print(obj["Key"])
    return files_in_bucket


bucket_name = "casrecmigration"
region = "eu-west-1"

drop_bucket(bucket_name, s3_session)

bucket_exists = False
for bucket in list_buckets(s3_session, region):
    if bucket_name == bucket:
        bucket_exists = True
if not bucket_exists:
    create_bucket(bucket_name, s3_session, region)
else:
    print("bucket exists")

anon_data_dir = "./anon_data"

for file in os.listdir(anon_data_dir):
    file_path = f".{anon_data_dir}/{file}"
    s3_file_path = f"{file}"
    upload_file(bucket_name, file_path, s3_session, s3_file_path)

list_bucket_contents(bucket_name, s3_session)
