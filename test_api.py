# -*- coding: utf-8 -*-
import requests

url = "https://openlibrary.org/search.json"
params = {"q": "fiction", "limit": 5}
r = requests.get(url, params=params, timeout=60,
                 headers={"User-Agent": "cs200-student-project"})
print("Status:", r.status_code)
print(r.text[:600])
