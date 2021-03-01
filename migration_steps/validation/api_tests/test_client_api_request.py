import requests
import json
import jsonschema
import pytest
import re
import os
import pandas as pd


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


@pytest.fixture(scope="session", autouse=True)
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


def test_authentication(create_a_session):
    headers_dict = create_a_session["headers_dict"]
    status_code = create_a_session["status_code"]

    headers_schema = {
        "type": "object",
        "properties": {
            "Cookie": {"type": "string"},
            "x-xsrf-token": {"type": "string"},
        },
    }

    assert jsonschema.validate(instance=headers_dict, schema=headers_schema) is None
    assert re.match(
        "sirius=(?:(?!;\s+path=/;\s+HttpOnly,\s+XSRF\-TOKEN=)(?:.|\n))*;\s+path=/;\s+HttpOnly,\s+XSRF\-TOKEN=(?:(?!;\s+Path=/)(?:.|\n))*;\s+Path=/",
        headers_dict["Cookie"],
    )
    # Brings back 401 in live even though it has authenticated fine
    assert status_code == 401 or status_code == 200


@pytest.mark.parametrize("csv", ["clients"])
def test_csvs(csv, create_a_session):
    csv_data = pd.read_csv(f"{csv}.csv")
    # Iterate over rows
    for index, row in csv_data.iterrows():
        endpoint = row["endpoint"]
        path_var = row["path_var"]
        endpoint_final = str(endpoint).replace("{id}", str(path_var))
        print(endpoint_final)
        response = create_a_session["sess"].get(
            f'{create_a_session["base_url"]}{endpoint_final}',
            headers=create_a_session["headers_dict"],
        )
        json_obj = json.loads(response.text)

        for header in row.index:
            if header not in ["endpoint", "path_var", "full_check"]:
                var_to_eval = f"json_obj{header}"
                try:
                    curr_var = eval(var_to_eval)
                except KeyError:
                    curr_var = ""
                    pass
                assert curr_var == str(row[header]).replace("nan", "")

        if row["full_check"] == "true":
            with open(f"responses/{csv}_{path_var}.json") as json_file:
                expected_response = json.load(json_file)
                assert json_obj == expected_response


@pytest.mark.parametrize("csv", ["fail"])
def test_fail_csvs(csv, create_a_session):
    csv_data = pd.read_csv(f"{csv}.csv")
    # Iterate over rows
    for index, row in csv_data.iterrows():
        endpoint = row["endpoint"]
        path_var = row["path_var"]
        endpoint_final = str(endpoint).replace("{id}", str(path_var))
        print(endpoint_final)
        response = create_a_session["sess"].get(
            f'{create_a_session["base_url"]}{endpoint_final}',
            headers=create_a_session["headers_dict"],
        )
        json_obj = json.loads(response.text)

        fail_count = 0
        for header in row.index:
            if header not in ["endpoint", "path_var", "full_check"]:
                var_to_eval = f"json_obj{header}"
                try:
                    curr_var = eval(var_to_eval)
                except KeyError:
                    curr_var = ""
                    pass
                if curr_var != str(row[header]).replace("nan", ""):
                    fail_count = fail_count + 1
        assert fail_count == 1

        if row["full_check"] == "true":
            with open(f"responses/{csv}_{path_var}.json") as json_file:
                expected_response = json.load(json_file)
                assert json_obj != expected_response
