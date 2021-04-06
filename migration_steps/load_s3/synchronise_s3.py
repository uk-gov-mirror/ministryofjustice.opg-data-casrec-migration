import time
import boto3
import os
import shutil
from pathlib import Path

current_path = Path(os.path.dirname(os.path.realpath(__file__)))


def operator_session():

    client = boto3.client("sts")

    role_to_assume = f"arn:aws:iam::288342028542:role/operator"
    response = client.assume_role(
        RoleArn=role_to_assume, RoleSessionName="assumed_role"
    )

    session = boto3.Session(
        aws_access_key_id=response["Credentials"]["AccessKeyId"],
        aws_secret_access_key=response["Credentials"]["SecretAccessKey"],
        aws_session_token=response["Credentials"]["SessionToken"],
    )

    return session


def get_list_of_files(bucket_name, s3, local_data_path):
    resp = s3.list_objects_v2(Bucket=bucket_name)
    files_in_bucket = []

    for obj in resp["Contents"]:
        file_and_folder = obj["Key"]
        folder = file_and_folder.split("/")[0]
        file = file_and_folder.split("/")[1]
        dl_file_location = str(local_data_path) + "/" + file
        if folder == "anon" and file.endswith(".csv"):
            s3.download_file(bucket_name, file_and_folder, dl_file_location)
            print(file_and_folder)
            files_in_bucket.append(file_and_folder)

    print(f"Total files returned: {len(files_in_bucket)}")
    return files_in_bucket


def clear_folder(folder):
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print("Failed to delete %s. Reason: %s" % (file_path, e))


def main():
    csv_dir_suffix = os.getenv("CSV_DIR_SUFFIX")
    bucket = "casrec-migration-development"
    s3_session = operator_session()
    s3 = s3_session.client("s3")
    local_data_path = current_path / csv_dir_suffix
    clear_folder(local_data_path)

    get_list_of_files(bucket, s3, local_data_path)


if __name__ == "__main__":
    t = time.process_time()
    main()
    print(f"Total time: {round(time.process_time() - t, 2)}")
