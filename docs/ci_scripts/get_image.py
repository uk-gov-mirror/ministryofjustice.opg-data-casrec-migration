import boto3
import click


def assume_aws_session(account, role):
    """
    Assume an AWS session so that we can access AWS resources as that account
    """

    client = boto3.client("sts")
    role_to_assume = f"arn:aws:iam::{account}:role/{role}"
    response = client.assume_role(
        RoleArn=role_to_assume, RoleSessionName="assumed_role"
    )

    session = boto3.Session(
        aws_access_key_id=response["Credentials"]["AccessKeyId"],
        aws_secret_access_key=response["Credentials"]["SecretAccessKey"],
        aws_session_token=response["Credentials"]["SessionToken"],
    )

    return session


@click.command()
@click.option("--role", default="operator")
def main(role):
    account = "311462405659"
    region = "eu-west-1"
    ecr_session = assume_aws_session(account, role)
    client = ecr_session.client("ecr", region_name=region)
    response = client.describe_images(repositoryName="casrec-migration/etl0")
    latest = None
    for images in response["imageDetails"]:
        if "imageTags" in images:
            if "master" in images["imageTags"][0]:
                if latest is None:
                    latest = images["imagePushedAt"]
                    image = images["imageTags"][0]
                elif images["imagePushedAt"] > latest:
                    latest = images["imagePushedAt"]
                    image = images["imageTags"][0]
    print(image)


if __name__ == "__main__":
    main()
