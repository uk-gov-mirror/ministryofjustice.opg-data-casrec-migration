import requests
import json
import click
import time


def get_running_jobs(
    circle_builds_token, circle_project_username, circle_project_reponame
):
    running_jobs_url = f"https://circleci.com/api/v1.1/project/github/{circle_project_username}/{circle_project_reponame}?circle-token={circle_builds_token}"
    response = requests.get(running_jobs_url)
    running_jobs = []
    if response.status_code == 200:
        running_jobs_json = json.loads(response.text)

        for job in running_jobs_json:
            if job["status"] == "failed" or job["status"] == "running":
                print(f"\"{job['workflows']['job_name']}\" is \"{job['status']}\"")
                running_jobs.append(job["workflows"]["job_name"])

        return running_jobs
    else:
        print(f"API call to circle failed with status code: {response.status_code}")
        return running_jobs


@click.command()
@click.option("--circle_builds_token", default=None)
@click.option("--circle_project_username", default=None)
@click.option("--circle_project_reponame", default=None)
def main(circle_builds_token, circle_project_username, circle_project_reponame):
    time_taken = 0
    secs = 10
    while (
        len(
            get_running_jobs(
                circle_builds_token, circle_project_username, circle_project_reponame
            )
        )
        > 0
    ):
        time.sleep(secs)
        time_taken += secs
        print(f"Waited {time_taken} seconds for previous job to finish")
    print("Nothing currently running")


if __name__ == "__main__":
    main()
