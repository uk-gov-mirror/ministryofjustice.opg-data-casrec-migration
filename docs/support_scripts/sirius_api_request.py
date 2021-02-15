import requests


response = requests.get("http://frontend:8080/auth/login")

print(response.status_code)
cookie = response.headers["Set-Cookie"]
xsrf = response.headers["X-XSRF-TOKEN"]

print(cookie)
print(xsrf)

headers_dict = {"Cookie": cookie, "x-xsrf-token": xsrf}
# data = {"email": "case.manager@opgtest.com", "password": "FAKEPW"}

with requests.Session() as s:
    p = s.post("http://frontend:8080/auth/login", data=data, headers=headers_dict)
    # print the html returned or something more intelligent to see if it's a successful login page.
    print(p.status_code)
    # print(p.headers)
    #
    # # An authorised request.
    # r = s.get('http://frontend:8080/supervision')
    #
    # print(r.status_code)
    #
    r = s.get("http://frontend:8080/api/v1/clients/45", headers=headers_dict)
    print(r.text)
    #
    print(s.cookies.get_dict())
    # print(s.auth)
    # print(s.headers)


#
# print(response.headers)
# print(response.content)
# print(response.status_code)
# print(response.cookies)
# print(response.request)

# curl -i --location --request GET 'http://frontend:8080/api/v1/clients/45' \
# --header 'x-xsrf-token: UGolw9tmdfakj7o/F9ubtg==' \
# --header 'Cookie: sirius=8nulr09bcrhpi4nkfcf7cukksj; XSRF-TOKEN=UGolw9tmdfakj7o%2FF9ubtg%3D%3D' \
