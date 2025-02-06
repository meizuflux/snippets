from urllib.request import Request, urlopen
import json

api_key = " 9:jK0nRR1Vq8cU5OVuxydt7y1bTIDcP1I1ZWNxv3WzBgWWpnRbtmfdXBSzE8Fr3LPlNuIEoEAG4n7fm0usiImeUtgWuZYnnCY0oICu2gbDTzn6xwv2mZshroFCpGr4MUcm"
url = "http://localhost:8000/api/v1/auth/about"
headers = {"apiKey": api_key}

req = Request(url, headers=headers)

with urlopen(req) as response:
    data = json.load(response)
    print(data)