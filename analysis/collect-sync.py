import sys
sys.path.insert(0, "./vendor")
import requests

def handler():
    r = requests.get("https://www.viniciusbarros.info")
    print(r.status_code)
    print(r.headers)


handler()

