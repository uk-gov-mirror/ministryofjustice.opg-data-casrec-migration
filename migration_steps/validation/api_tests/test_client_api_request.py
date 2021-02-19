import requests
import json
import jsonschema
import pytest
import re
import os


def get_session(base_url):
    response = requests.get(base_url)
    cookie = response.headers["Set-Cookie"]
    xsrf = response.headers["X-XSRF-TOKEN"]
    headers_dict = {"Cookie": cookie, "x-xsrf-token": xsrf}
    data = {
        "email": "case.manager@opgtest.com",
        "password": "Password1",  # pragma: allowlist secret
    }
    with requests.Session() as s:
        p = s.post(f"{base_url}/auth/login", data=data, headers=headers_dict)
        print(f"Login returns: {p.status_code}")
        return s, headers_dict, p.status_code


@pytest.fixture(scope="session", autouse=True)
def create_a_session():
    base_url = os.environ.get("SIRIUS_FRONT_URL")
    sess, headers_dict, status_code = get_session(base_url)
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
    assert status_code == 401


@pytest.mark.parametrize("client_id", [73])
def test_client(client_id, create_a_session):
    r = create_a_session["sess"].get(
        f"{create_a_session['base_url']}/api/v1/clients/{client_id}",
        headers=create_a_session["headers_dict"],
    )
    json_obj = json.loads(r.text)

    with open("client.schema.json", "r") as json_file:
        json_schema_obj = json.load(json_file)

    assert jsonschema.validate(instance=json_obj, schema=json_schema_obj) is None
