import requests
import json
import pandas as pd
import os

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


csvs = ["clients"]

for csv in csvs:
    csv_data = pd.read_csv(f"{csv}.csv")
    columns = csv_data.columns.tolist()
    conn = create_a_session()
    # Iterate over rows
    for index, row in csv_data.iterrows():
        endpoint = row["endpoint"]
        path_var = row["path_var"]
        endpoint_final = str(endpoint).replace("{id}", str(path_var))
        print(endpoint_final)
        response = conn["sess"].get(
            f'{conn["base_url"]}{endpoint_final}', headers=conn["headers_dict"],
        )
        json_obj = json.loads(response.text)
        with open(f"responses/{csv}_{path_var}.json", "w") as outfile:
            json.dump(json_obj, outfile, indent=4, sort_keys=False)
