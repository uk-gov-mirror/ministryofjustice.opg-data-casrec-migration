import requests
import json
import jsonschema


def get_session():
    response = requests.get("http://frontend:8080")
    cookie = response.headers["Set-Cookie"]
    xsrf = response.headers["X-XSRF-TOKEN"]
    headers_dict = {"Cookie": cookie, "x-xsrf-token": xsrf}
    data = {}
    # {"email": "case.manager@opgtest.com", "password": "FAKE"}
    with requests.Session() as s:
        p = s.post("http://frontend:8080/auth/login", data=data, headers=headers_dict)
        print(f"Login returns: {p.status_code}")
        return s, headers_dict


def pp_json(json_thing, sort=True, indents=4):
    if type(json_thing) is str:
        print(json.dumps(json.loads(json_thing), sort_keys=sort, indent=indents))
    else:
        print(json.dumps(json_thing, sort_keys=sort, indent=indents))
    return None


sess, headers_dict = get_session()
r = sess.get("http://frontend:8080/api/v1/clients/45", headers=headers_dict)
json_obj = json.loads(r.text)

with open("client.schema.json", "r") as json_file:
    json_schema_obj = json.load(json_file)

response = jsonschema.validate(instance=json_obj, schema=json_schema_obj)

print(response)

with open("client.json", "w") as outfile:
    json.dump(json_obj, outfile, indent=4, sort_keys=True)

    #
    # r = s.get("http://frontend:8080/api/v1/clients/45/annual-reports", headers=headers_dict)
