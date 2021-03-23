import requests
import json
import pandas as pd
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

current_path = Path(os.path.dirname(os.path.realpath(__file__)))
sys.path.insert(0, str(current_path) + "/../../../migration_steps/shared")
from helpers import *

env_path = current_path / "../../../migration_steps/.env"
load_dotenv(dotenv_path=env_path)
base_url = os.environ.get("SIRIUS_FRONT_URL")
password = os.environ.get("API_TEST_PASSWORD")
environment = os.environ.get("ENVIRONMENT")
# This is just a little helper script for
# generating response json from CSV inputs to use in our tests


def get_session(base_url, user, password):
    response = requests.get(base_url)
    cookie = response.headers["Set-Cookie"]
    xsrf = response.headers["X-XSRF-TOKEN"]
    headers_dict = {"Cookie": cookie, "x-xsrf-token": xsrf}
    data = {"email": user, "password": password}
    with requests.Session() as s:
        p = s.post(f"{base_url}/auth/login", data=data, headers=headers_dict)
        print(f"Login returns: {p.status_code}")
        return s, headers_dict, p.status_code


def create_a_session():
    base_url = os.environ.get("SIRIUS_FRONT_URL")
    user = "case.manager@opgtest.com"
    password = os.environ.get("API_TEST_PASSWORD")
    sess, headers_dict, status_code = get_session(base_url, user, password)
    session = {
        "sess": sess,
        "headers_dict": headers_dict,
        "status_code": status_code,
        "base_url": base_url,
    }

    return session


def get_entity_id(session, entity, search_field, search_value):
    extra_headers = {"content-type": "application/json"}
    full_headers = {**session["headers_dict"], **extra_headers}

    data_raw = {
        "from": 0,
        "index": entity,
        "query": {
            "simple_query_string": {
                "query": search_value,
                "fields": ["searchable", search_field],
                "default_operator": "AND",
            }
        },
        "size": 5,
    }

    response = session["sess"].post(
        f'{session["base_url"]}/api/advanced-search',
        headers=full_headers,
        data=json.dumps(data_raw),
    )
    search_result = json.loads(response.text)
    entity_id = None
    if search_result["hits"]["total"] > 0:
        entity_id = search_result["hits"]["hits"][0]["_id"]

    return entity_id


headers = [
    '["firstname"]',
    '["surname"]',
    '["otherNames"]',
    '["addressLine1"]',
    '["addressLine2"]',
    '["addressLine3"]',
    '["town"]',
    '["county"]',
    '["postcode"]',
    '["country"]',
    '["phoneNumber"]',
    '["correspondenceByPost"]',
    '["correspondenceByPhone"]',
    '["correspondenceByEmail"]',
    '["personType"]',
    '["clientStatus"]["handle"]',
    '["clientStatus"]["label"]',
    '["clientAccommodation"]["handle"]',
    '["clientAccommodation"]["label"]',
    '["supervisionCaseOwner"]["name"]',
    '["supervisionCaseOwner"]["phoneNumber"]',
    '["maritalStatus"]',
]
csvs = ["clients"]

search_headers = [
    "endpoint",
    "entity_ref",
    "search_entity",
    "search_field",
    "full_check",
]

for csv in csvs:
    head_line = ""
    for header in search_headers:
        head_line = head_line + header + ","
    for header in headers:
        head_line = head_line + header + ","
    head_line = head_line[:-1]
    head_line = head_line + "\n"

    print(head_line)

    with open(f"responses/{csv}_output.csv", "w") as csv_outfile:
        csv_outfile.write(head_line)

    csv_data = pd.read_csv(f"{csv}.csv", dtype=str)
    columns = csv_data.columns.tolist()
    conn = create_a_session()

    # Iterate over rows
    for index, row in csv_data.iterrows():
        endpoint = row["endpoint"]
        entity_ref = row["entity_ref"]
        search_entity = row["search_entity"]
        search_field = row["search_field"]
        entity_id = get_entity_id(conn, search_entity, search_field, entity_ref)
        endpoint_final = str(endpoint).replace("{id}", str(entity_id))
        print(endpoint_final)
        response = conn["sess"].get(
            f'{conn["base_url"]}{endpoint_final}', headers=conn["headers_dict"],
        )
        json_obj = json.loads(response.text)
        with open(f"responses/{csv}_{entity_ref}.json", "w") as outfile:
            json.dump(json_obj, outfile, indent=4, sort_keys=False)

        line = ""
        for header in search_headers:
            curr_var = eval(f'row["{header}"]')
            line = line + str(curr_var) + ","
        for header in headers:
            var_to_eval = f"json_obj{header}"
            try:
                curr_var = eval(var_to_eval)
                if curr_var is None:
                    curr_var = ""
                else:
                    curr_var = str(curr_var)
            except KeyError:
                curr_var = ""
                pass

            line = line + curr_var + ","
        line = line[:-1]
        line = line + "\n"
        print(line)
        with open(f"responses/{csv}_output.csv", "a") as csv_outfile:
            csv_outfile.write(line)
